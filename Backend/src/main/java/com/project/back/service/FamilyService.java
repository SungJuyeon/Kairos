package com.project.back.service;

import com.project.back.entity.FamilyRequest;
import com.project.back.entity.Familyship;
import com.project.back.entity.UserEntity;
import com.project.back.repository.FamilyRequestRepository;
import com.project.back.repository.FamilyshipRepository;
import com.project.back.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class FamilyService {
    private final FamilyRequestRepository familyRequestRepository;
    private final FamilyshipRepository familyshipRepository;
    private final UserRepository userRepository;

    //가족 요청 보내기
    public FamilyRequest sendFamilyRequest(Long senderId, String receiverUsername){
        UserEntity sender = userRepository.findById(senderId).orElseThrow(() -> new RuntimeException("SenderId not found"));
        UserEntity receiver = userRepository.findByUsername(receiverUsername);

        FamilyRequest familyRequest = new FamilyRequest();
        familyRequest.setSender(sender);
        familyRequest.setReceiver(receiver);
        familyRequest.setStatus(FamilyRequest.FamilyRequestStatus.PENDING);

        return familyRequestRepository.save(familyRequest);
    }

    //가족 요청 수락
    public Familyship acceptFamilyRequest(Long requestId){
        FamilyRequest request = familyRequestRepository.findById(requestId)
                .orElseThrow(() -> new RuntimeException("FamilyRequest not found"));

        request.setStatus(FamilyRequest.FamilyRequestStatus.ACCEPTED);
        familyRequestRepository.save(request);

        Familyship familyship = new Familyship();
        familyship.setUser1(request.getSender());
        familyship.setUser2(request.getReceiver());

        return familyshipRepository.save(familyship);
    }
    public List<UserEntity> getFamily(Long userId) {
        return familyshipRepository.findFamilyByUserId(userId);
    }


    //가족 목록 가져오기
//    public List<Familyship> getFamily(Long userId){
//        UserEntity user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("User not found"));
//        return familyshipRepository.findByUser1OrUser2(user, user);
//    }

    public List<FamilyRequest> getSentRequests(Long senderId) {
        return familyRequestRepository.findBySender_Id(senderId);
    }

    public List<FamilyRequest> getReceivedRequests(Long receiverId) {
        return familyRequestRepository.findByReceiver_Id(receiverId);
    }

}
