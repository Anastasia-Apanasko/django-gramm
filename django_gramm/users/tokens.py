from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AppTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.is_active}{user.pk}{timestamp}"


account_activation_token = AppTokenGenerator()