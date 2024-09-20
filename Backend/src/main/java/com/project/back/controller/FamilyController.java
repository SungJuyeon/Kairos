package com.project.back.controller;

import com.project.back.dto.FamilyRequestDTO;
import com.project.back.dto.FamilyUserDTO;
import com.project.back.entity.FamilyRequest;
import com.project.back.entity.Familyship;
import com.project.back.entity.UserEntity;
import com.project.back.repository.UserRepository;
import com.project.back.service.FamilyService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/family")
@RequiredArgsConstructor
public class FamilyController {
    private final FamilyService familyService;
    private final UserRepository userRepository;  // UserRepository를 주입받습니다.

    // 로그인 된 사용자가 가족 요청할 사람의 유저 네임 받고 여기에 전달
    //senderUsername, receiverUsername
    @PostMapping("/request")
    public FamilyRequest sendFamilyRequest(@RequestBody FamilyRequestDTO request) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String senderUsername = authentication.getName();  // 현재 로그인한 사용자의 username

        UserEntity sender = userRepository.findByUsername(senderUsername);
        if (sender == null) {
            throw new RuntimeException("User not found");
        }
        Long senderId = sender.getId();  // UserEntity에서 ID를 얻기
        String receiverUsername = request.getReceiverUsername();
        UserEntity receiver = userRepository.findByUsername(receiverUsername);
        return familyService.sendFamilyRequest(senderId, receiver.getId());
    }


    // URL 쿼리 파라미터 http://localhost:8080/family/accept?requestId=2902 형식으로 요청받음
    // requestId 는 /requests/received 에서 확인
    // 수락 하는 것
    @PostMapping("/request/accept")
    public ResponseEntity<String> acceptFamilyRequest(@RequestParam(name = "requestId") Long requestId) {
        System.out.println("Attempting to accept family request with ID: " + requestId);
        try {
            familyService.acceptFamilyRequest(requestId);
            return ResponseEntity.ok("Family request accepted successfully.");
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Family request not found.");
        }
    }

    // accept랑 완전 반대, 거절하는 것
    @PostMapping("/request/reject")
    public ResponseEntity<String> rejectFamilyRequest(@RequestParam(name = "requestId") Long requestId) {
        System.out.println("Attempting to accept family request with ID: " + requestId);
        try {
            familyService.rejectFamilyRequest(requestId);
            return ResponseEntity.ok("Family request rejected successfully.");
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Family request not found.");
        }
    }

    // 가족들 리스트, 닉네일과 포토네임(사진)만 전달
    @GetMapping("/list")
    public List<FamilyUserDTO> getFamily(){
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();  // 현재 로그인한 사용자의 username

        UserEntity user = userRepository.findByUsername(username);
        if (user == null) {
            throw new RuntimeException("User not found");
        }

        List<UserEntity> family = familyService.getFamily(user.getId());
        return family.stream()
                .map(familyName -> new FamilyUserDTO(familyName.getNickname(), familyName.getPhotoname()))
                .collect(Collectors.toList());
    }

    //사용자가 보낸 친구 요청들을 조회
    // requesrId, senderUsername, receiverUsername, status 들이 옴
    @GetMapping("/requests/sent")
    public ResponseEntity<List<FamilyRequestDTO>> getSentRequests() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String senderUsername = authentication.getName();  // 현재 로그인한 사용자의 username

        UserEntity sender = userRepository.findByUsername(senderUsername);
        if (sender == null) {
            return ResponseEntity.notFound().build();
        }

        List<FamilyRequest> sentRequests = familyService.getSentRequests(sender.getId());
        List<FamilyRequestDTO> requestDTOs = sentRequests.stream()
                .map(request -> new FamilyRequestDTO(
                        request.getId(),
                        request.getReceiver().getUsername(),
                        request.getSender().getUsername(),
                        request.getStatus().name()
                ))
                .collect(Collectors.toList());

        return ResponseEntity.ok(requestDTOs);
    }


    //사용자가 받은 친구 요청들을 조회
    // requestId를 여기서 가져옴
    // requesrId, senderUsername, receiverUsername, status 들이 옴
    @GetMapping("/requests/received")
    public ResponseEntity<List<FamilyRequestDTO>> getReceivedRequests() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String receiverUsername = authentication.getName();  // 현재 로그인한 사용자의 username

        UserEntity receiver = userRepository.findByUsername(receiverUsername);
        if (receiver == null) {
            return ResponseEntity.notFound().build();
        }

        List<FamilyRequest> receivedRequests = familyService.getReceivedRequests(receiver.getId());
        List<FamilyRequestDTO> requestDTOs = receivedRequests.stream()
                .map(request -> new FamilyRequestDTO(
                        request.getId(),
                        request.getSender().getUsername(),
                        request.getSender().getUsername(),
                        request.getStatus().name()
                ))
                .collect(Collectors.toList());

        return ResponseEntity.ok(requestDTOs);
    }

}

