from rest_framework.routers import DefaultRouter

from apps.admissao.views import ChecklistItemAdmissaoViewSet, FuncionarioViewSet

router = DefaultRouter()
router.register("funcionarios", FuncionarioViewSet, basename="funcionario")
router.register("checklist-admissao", ChecklistItemAdmissaoViewSet, basename="checklist-admissao")

urlpatterns = router.urls
