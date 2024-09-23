package com.project.back.controller;

import com.project.back.dto.FamilyRequestDTO;
import com.project.back.dto.FamilyUserDTO;
import com.project.back.entity.FamilyRequest;
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
        if (receiver == null) {
            throw new RuntimeException("Receiver user not found");
        }
        return familyService.sendFamilyRequest(senderId, receiver.getId());
    }

    // 가족 요청 수락
    @PostMapping("/request/accept")
    public ResponseEntity<String> acceptFamilyRequest(@RequestParam(name = "requestId") Long requestId) {
        System.out.println("Attempting to accept family request with ID: " + requestId);
        try {
            familyService.acceptFamilyRequest(requestId);
            return ResponseEntity.ok("Family request accepted and connections updated successfully.");
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(e.getMessage());
        }
    }

    // 가족 요청 거절
    @PostMapping("/request/reject")
    public ResponseEntity<String> rejectFamilyRequest(@RequestParam(name = "requestId") Long requestId) {
        System.out.println("Attempting to reject family request with ID: " + requestId);
        try {
            familyService.rejectFamilyRequest(requestId);
            return ResponseEntity.ok("Family request rejected successfully.");
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(e.getMessage());
        }
    }

    // 가족 목록 조회
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
                .map(familyMember -> new FamilyUserDTO(familyMember.getNickname(), familyMember.getPhotoname()))
                .collect(Collectors.toList());
    }

    // 사용자가 보낸 가족 요청들을 조회
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
                        request.getSender().getUsername(),
                        request.getReceiver().getUsername(),
                        request.getStatus().name()
                ))
                .collect(Collectors.toList());

        return ResponseEntity.ok(requestDTOs);
    }

    // 사용자가 받은 가족 요청들을 조회
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
                        request.getReceiver().getUsername(),
                        request.getStatus().name()
                ))
                .collect(Collectors.toList());

        return ResponseEntity.ok(requestDTOs);
    }

    // delete 로 http://localhost:8080/family/delete?memberUsername=3
    @DeleteMapping("/delete")
    public ResponseEntity<String> deleteFamilyMember(@RequestParam(name = "memberUsername") String memberUsername) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String currentUsername = authentication.getName();  // 현재 로그인한 사용자의 username

        UserEntity currentUser = userRepository.findByUsername(currentUsername);
        if (currentUser == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Current user not found.");
        }

        UserEntity member = userRepository.findByUsername(memberUsername);
        if (member == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Member user not found.");
        }

        try {
            familyService.deleteFamilyMember(currentUser.getId(), member.getId());
            return ResponseEntity.ok("Family member deleted successfully.");
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(e.getMessage());
        }
    }

}
