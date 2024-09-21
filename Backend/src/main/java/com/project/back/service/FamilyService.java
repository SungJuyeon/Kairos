package com.project.back.service;

import com.project.back.entity.FamilyRequest;
import com.project.back.entity.Familyship;
import com.project.back.entity.UserEntity;
import com.project.back.repository.FamilyRequestRepository;
import com.project.back.repository.FamilyshipRepository;
import com.project.back.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@Service
@RequiredArgsConstructor
public class FamilyService {
    private final FamilyRequestRepository familyRequestRepository;
    private final FamilyshipRepository familyshipRepository;
    private final UserRepository userRepository;

    // 가족 요청 보내기
    public FamilyRequest sendFamilyRequest(Long senderId, Long receiverId){
        UserEntity sender = userRepository.findById(senderId).orElseThrow(() -> new RuntimeException("Sender not found"));
        UserEntity receiver = userRepository.findById(receiverId).orElseThrow(() -> new RuntimeException("Receiver not found"));

        FamilyRequest familyRequest = new FamilyRequest();
        familyRequest.setSender(sender);
        familyRequest.setReceiver(receiver);
        familyRequest.setStatus(FamilyRequest.FamilyRequestStatus.PENDING);

        return familyRequestRepository.save(familyRequest);
    }

    // 가족 요청 수락
    @Transactional
    public void acceptFamilyRequest(Long requestId) {
        FamilyRequest request = familyRequestRepository.findById(requestId)
                .orElseThrow(() -> new RuntimeException("FamilyRequest not found"));

        request.setStatus(FamilyRequest.FamilyRequestStatus.ACCEPTED);
        familyRequestRepository.save(request);

        UserEntity sender = request.getSender();
        UserEntity receiver = request.getReceiver();

        // 사용자 간의 가족 관계 추가 (일관된 순서 유지)
        addFamilyship(sender, receiver);

        // 기존 가족 구성원 가져오기 (sender의 모든 연결된 사용자)
        Set<UserEntity> existingFamily = getAllConnectedUsers(sender.getId());

        // 새로운 가족 구성원(receiver)을 기존 가족 구성원과 연결
        existingFamily.forEach(user -> {
            if (!user.equals(sender) && !user.equals(receiver)) {
                addFamilyship(receiver, user);
            }
        });

        // 요청을 삭제하려면 아래 주석을 해제하세요
        familyRequestRepository.delete(request);
    }

    // 가족 요청 거절
    @Transactional
    public void rejectFamilyRequest(Long requestId) {
        FamilyRequest request = familyRequestRepository.findById(requestId)
                .orElseThrow(() -> new RuntimeException("FamilyRequest not found"));

        request.setStatus(FamilyRequest.FamilyRequestStatus.REJECTED);
        familyRequestRepository.save(request);

        // 요청을 삭제하려면 아래 주석을 해제하세요
        familyRequestRepository.delete(request);
    }

    // 사용자 간의 가족 관계 추가 (중복 방지)
    private void addFamilyship(UserEntity user1, UserEntity user2) {
        if (user1 != null && user2 != null && !user1.equals(user2)) {
            // 사용자 ID 순서에 따라 user1과 user2를 설정 (일관성 유지)
            if (user1.getId() > user2.getId()) {
                UserEntity temp = user1;
                user1 = user2;
                user2 = temp;
            }

            // 중복된 Familyship이 있는지 확인
            boolean exists = familyshipRepository.existsFamilyship(user1, user2);
            if (!exists) {
                Familyship familyship = new Familyship();
                familyship.setUser1(user1);
                familyship.setUser2(user2);
                familyshipRepository.save(familyship);
            }
        }
    }

    /**
     * 주어진 사용자 ID와 연결된 모든 가족 구성원을 반환하는 메서드
     * @param userId 사용자 ID
     * @return 연결된 모든 사용자 집합
     */
    private Set<UserEntity> getAllConnectedUsers(Long userId) {
        Set<UserEntity> connectedUsers = new HashSet<>();
        Queue<UserEntity> toVisit = new LinkedList<>();
        Set<Long> visited = new HashSet<>();

        UserEntity startUser = userRepository.findById(userId).orElse(null);
        if (startUser == null) return connectedUsers;

        toVisit.add(startUser);
        visited.add(startUser.getId());

        while (!toVisit.isEmpty()) {
            UserEntity current = toVisit.poll();
            connectedUsers.add(current);

            List<Familyship> familyships = familyshipRepository.findByUser1Id(current.getId());
            familyships.addAll(familyshipRepository.findByUser2Id(current.getId()));

            for (Familyship familyship : familyships) {
                UserEntity connectedUser = familyship.getUser1().equals(current) ? familyship.getUser2() : familyship.getUser1();
                if (!visited.contains(connectedUser.getId())) {
                    toVisit.add(connectedUser);
                    visited.add(connectedUser.getId());
                }
            }
        }

        return connectedUsers;
    }

    // 사용자의 가족 목록 가져오기
    public List<UserEntity> getFamily(Long userId) {
        List<Familyship> familyshipsAsUser1 = familyshipRepository.findByUser1Id(userId);
        List<Familyship> familyshipsAsUser2 = familyshipRepository.findByUser2Id(userId);

        Set<UserEntity> familyMembers = new HashSet<>();
        for (Familyship familyship : familyshipsAsUser1) {
            familyMembers.add(familyship.getUser2());
        }
        for (Familyship familyship : familyshipsAsUser2) {
            familyMembers.add(familyship.getUser1());
        }
        return new ArrayList<>(familyMembers);
    }

    public List<FamilyRequest> getSentRequests(Long senderId) {
        return familyRequestRepository.findBySender_Id(senderId);
    }

    public List<FamilyRequest> getReceivedRequests(Long receiverId) {
        return familyRequestRepository.findByReceiver_Id(receiverId);
    }

    // 가족 삭제
    @Transactional
    public void deleteFamilyMember(Long currentUserId, Long memberId) {
        UserEntity currentUser = userRepository.findById(currentUserId)
                .orElseThrow(() -> new RuntimeException("Current user not found"));
        UserEntity member = userRepository.findById(memberId)
                .orElseThrow(() -> new RuntimeException("Member user not found"));

        // 가족 관계 존재 확인
        boolean isFamily = familyshipRepository.existsFamilyship(currentUser, member);
        if (!isFamily) {
            throw new RuntimeException("The specified user is not a family member");
        }

        // 해당 사용자가 관련된 모든 Familyship 삭제
        List<Familyship> familyshipsToDelete = familyshipRepository.findByUser1Id(memberId);
        familyshipsToDelete.addAll(familyshipRepository.findByUser2Id(memberId));
        familyshipRepository.deleteAll(familyshipsToDelete);
    }
}
