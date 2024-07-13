package com.project.back.config;

import java.util.regex.Pattern;

public class PasswordUtils {

    private static final Pattern BCRYPT_PATTERN = Pattern.compile("\\A\\$2[ayb]\\$.{56}\\z");

    public static boolean isBCryptPassword(String password) {
        return BCRYPT_PATTERN.matcher(password).matches();
    }
}