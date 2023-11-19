from django.contrib.auth.base_user import BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self, username, email, user_id, password=None):
        if not email:
            raise ValueError("User must have an email")
        if not username:
            raise ValueError("User must have an username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            user_id=user_id,
        )

        user.set_password(password)
        # user.save(using=self.db)
        return user

    def create_superuser(self, username, email, user_id, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            user_id=user_id,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self.db)
        return user
