import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

from apps.core.managers import ActiveObjects, AllObjects


class TimeStampedModel(models.Model):
    """Base model do ecossistema. NUNCA modificar.

    Todo model de domínio herda daqui: id (UUID), company_id (multi-tenant,
    preenchido via utils.utils.capture_company_id), created_at, updated_at
    e active (soft delete — proibido usar .delete()).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    objects = ActiveObjects()
    all_objects = AllObjects()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def delete(self, *args, **kwargs):
        raise NotImplementedError(
            "Hard delete proibido. Use: instance.active = False; "
            'instance.save(update_fields=["active", "updated_at"])'
        )

    def soft_delete(self):
        self.active = False
        self.save(update_fields=["active", "updated_at"])


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.RH)
        extra_fields.setdefault("company_id", uuid.uuid4())
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser precisa de is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser precisa de is_superuser=True.")
        return self._create_user(email, password, **extra_fields)

    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class User(AbstractBaseUser, TimeStampedModel):
    """Usuário interno (RH / Gestor). Candidato tem model/auth próprios em
    apps.candidatos — não usa este model.
    """

    class Role(models.TextChoices):
        RH = "rh", "RH"
        GESTOR = "gestor", "Gestor"

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=10, choices=Role.choices)
    area = models.CharField(
        max_length=100,
        blank=True,
        help_text="Área do gestor, usada para escopar vagas/candidatos/processos.",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "role"]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class UserFunctionPermission(TimeStampedModel):
    """Concessão granular de RBAC: qual usuário pode ver/criar/editar/excluir
    em qual módulo (permission_path do ViewSet). Consultado por
    apps.core.permissions.HasFunctionPermission.
    """

    user = models.ForeignKey(User, related_name="function_permissions", on_delete=models.CASCADE)
    function = models.SlugField(max_length=100, help_text="Slug do módulo, ex: vagas, candidatos.")
    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "function"], name="unique_user_function_permission"
            )
        ]

    def __str__(self):
        return f"{self.user.email} · {self.function}"

    def save(self, *args, **kwargs):
        if not self.company_id:
            self.company_id = self.user.company_id
        super().save(*args, **kwargs)
