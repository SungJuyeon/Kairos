package com.project.back.service;

import com.project.back.dto.JoinDTO;
import com.project.back.entity.UserEntity;
import com.project.back.repository.UserRepository;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@AllArgsConstructor
public class JoinService {

    private final UserRepository userRepository;
    private final BCryptPasswordEncoder bCryptPasswordEncoder;

    public void joinProcess(JoinDTO joinDTO) {

        String username = joinDTO.getUsername();    //=loginId
        String password = joinDTO.getPassword();

        Boolean isExist = userRepository.existsByUsername(username);

        if (isExist) {  //이미 존재하는 login id
            return;
        }
        //회원가입 진행
        UserEntity user = new UserEntity();
        user.setUsername(username);
        user.setPassword(bCryptPasswordEncoder.encode(password));   //암호화 진행
        user.setRole("ADMIN");  //권한 설정 (관리자 계정 필요없으면 USER로 바꾸기)

        userRepository.save(user);
    }
}
