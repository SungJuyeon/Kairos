package com.project.back.service;

import com.project.back.entity.FamilyRequest;
import com.project.back.entity.Familyship;
import com.project.back.entity.UserEntity;
import com.project.back.repository.FamilyRequestRepository;
import com.project.back.repository.FamilyshipRepository;
import com.project.back.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

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
    public void acceptFamilyRequest(Long requestId) {
        FamilyRequest request = familyRequestRepository.findById(requestId)
                .orElseThrow(() -> new RuntimeException("FamilyRequest not found"));

        request.setStatus(FamilyRequest.FamilyRequestStatus.ACCEPTED);
        familyRequestRepository.save(request);

        UserEntity sender = request.getSender();
        UserEntity receiver = request.getReceiver();

        // 사용자 간의 가족 관계 추가
        addFamilyship(sender, receiver);

        // 추가적으로 연결된 사용자 모두와의 관계를 추가
        List<UserEntity> allConnectedUsers = getAllConnectedUsers(sender.getId());
        allConnectedUsers.addAll(getAllConnectedUsers(receiver.getId()));
        allConnectedUsers.forEach(user -> {
            if (!user.equals(sender) && !user.equals(receiver)) {
                addFamilyship(sender, user);
                addFamilyship(receiver, user);
            }
        });
    }

    //가족 요청 거절
    public void rejectFamilyRequest(Long requestId) {
        FamilyRequest request = familyRequestRepository.findById(requestId)
               .orElseThrow(() -> new RuntimeException("FamilyRequest not found"));

        request.setStatus(FamilyRequest.FamilyRequestStatus.REJECTED);
        familyRequestRepository.save(request);
    }

    private void addFamilyship(UserEntity user1, UserEntity user2) {
        if (user1 != null && user2 != null && !user1.equals(user2)) {
            // 중복된 Familyship이 있는지 확인
            boolean exists = familyshipRepository.existsByUser1AndUser2(user1, user2) || familyshipRepository.existsByUser1AndUser2(user2, user1);
            if (!exists) {
                Familyship familyship = new Familyship();
                familyship.setUser1(user1);
                familyship.setUser2(user2);
                familyshipRepository.save(familyship);
            }
        }
    }

    private List<UserEntity> getAllConnectedUsers(Long userId) {
        List<UserEntity> connectedUsers = new ArrayList<>();

        // 사용자에 대해 수락된 요청을 통해 연결된 모든 사용자 가져오기
        List<FamilyRequest> requests = familyRequestRepository.findBySender_Id(userId);
        for (FamilyRequest request : requests) {
            if (request.getStatus() == FamilyRequest.FamilyRequestStatus.ACCEPTED) {
                connectedUsers.add(request.getReceiver());
            }
        }

        return connectedUsers;
    }

    // 사용자의 가족 목록 가져오기
    public List<UserEntity> getFamily(Long userId) {
        return familyshipRepository.findFamilyByUserId(userId);
    }

    public List<FamilyRequest> getSentRequests(Long senderId) {
        return familyRequestRepository.findBySender_Id(senderId);
    }

    public List<FamilyRequest> getReceivedRequests(Long receiverId) {
        return familyRequestRepository.findByReceiver_Id(receiverId);
    }
}
