# Seguridad comercial y gobierno del sistema

## Roles

- `administrador`: alta de usuarios, entrenamiento, auditoría, gestión integral
- `supervisor`: lectura integral, resolución de alertas, auditoría
- `inspector`: gestión de incidentes y resolución de alertas
- `analista`: análisis, entrenamiento del modelo, lectura operativa

## Controles implementados

- JWT para sesión
- Verificación de roles en endpoints sensibles
- Auditoría de:
  - registro de usuario
  - inicio de sesión
  - creación y actualización de incidentes
  - creación y resolución de alertas
  - recuperación de acceso

## Recuperación de acceso

Endpoints:

- `POST /auth/password-reset/request`
- `POST /auth/password-reset/confirm`

En esta versión, el token se devuelve para uso administrativo o controlado.
Para producción comercial se recomienda integrarlo con correo corporativo.
