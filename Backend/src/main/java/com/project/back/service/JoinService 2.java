package com.project.back.service;

import com.project.back.dto.JoinDTO;
import com.project.back.entity.UserEntity;
import com.project.back.repository.UserRepository;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@Service
@AllArgsConstructor
public class JoinService {

    private final UserRepository userRepository;
    private final BCryptPasswordEncoder bCryptPasswordEncoder;

    public void joinProcess(JoinDTO joinDTO) throws IOException {

        String username = joinDTO.getUsername();    //=loginId
        String password = joinDTO.getPassword();
        String email = joinDTO.getEmail();
        String nickname = joinDTO.getNickname();
        Boolean isExist = userRepository.existsByUsername(username);
        Boolean isExistN = userRepository.existsByNickname(nickname);
        byte[] photoname = joinDTO.getPhotoname();

        if (isExist) {  //이미 존재하는 login id
            throw new IllegalArgumentException("이미 존재하는 아이디입니다.");
        }

        if (isExistN) {  //이미 존재하는 login id
            throw new IllegalArgumentException("이미 존재하는 닉네임입니다.");
        }
        //회원가입 진행
        UserEntity user = new UserEntity();
        user.setUsername(username);
        user.setPassword(bCryptPasswordEncoder.encode(password));   //암호화 진행
        user.setRole("ADMIN");  //권한 설정 (관리자 계정 필요없으면 USER로 바꾸기)

        user.setEmail(email);
        user.setNickname(nickname);
        user.setPhotoname(photoname);  // 바이트 배열 설정

        userRepository.save(user);
    }
}
