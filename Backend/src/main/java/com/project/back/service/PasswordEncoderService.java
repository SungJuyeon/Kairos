
package com.project.back.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

import com.project.back.config.PasswordUtils;
import com.project.back.entity.MemberEntity;
import com.project.back.repository.MemberRepository;

@Component
public class PasswordEncoderService {

    @Autowired
    private MemberRepository memberRepository;

    @Autowired
    private BCryptPasswordEncoder bCryptPasswordEncoder;

    public void encodePasswords() {
        Iterable<MemberEntity> users = memberRepository.findAll();

        for (MemberEntity user : users) {
            String rawPassword = user.getPw();
            if (!PasswordUtils.isBCryptPassword(rawPassword)) {
                String encodedPassword = bCryptPasswordEncoder.encode(rawPassword);
                user.setPw(encodedPassword);
                memberRepository.save(user);
            }
        }
    }
}
