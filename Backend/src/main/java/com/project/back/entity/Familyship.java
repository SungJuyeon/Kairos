package com.project.back.entity;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Data
public class Familyship {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "user1_id")
    private UserEntity user1;

    @ManyToOne
    @JoinColumn(name = "user2_id")
    private UserEntity user2;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Familyship)) return false;
        Familyship that = (Familyship) o;
        return (user1.equals(that.user1) && user2.equals(that.user2)) ||
                (user1.equals(that.user2) && user2.equals(that.user1));
    }

    @Override
    public int hashCode() {
        return 31 * user1.hashCode() + user2.hashCode();
    }
}
