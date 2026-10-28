-- Primero registra una cuenta normal desde la página /registro.
-- Después ejecuta esta consulta sustituyendo el correo por el correo
-- exacto de esa cuenta. Solo el administrador del servidor debe hacerlo.
USE conoce_tenango;
UPDATE usuarios SET rol='admin' WHERE correo='correo-del-admin@ejemplo.com';
-- Cierra sesión e inicia sesión de nuevo para que se actualice el rol.
