# RasDom

Este proyecto usará una Raspberry Pi 3B como gestor de doméstico y control de intrusiones.
El sistema recoge el tiempo a través de la API de OpenWeather y en fución de los valores toma decisiones
que recaen en la capa Mock que es la que se encargaría de controlar los sistemas de la casa, como calefacción,aspiradora...
Por otro lado también tiene un sensor de movimiento que cuando se activa toma una instantátea con la cámara.
Toda esta información se la envía a un servidor, para que éste lo guarde. La implementación del servidor está en el proyecto NodeDom.

Este proyecto todavía no está terminado, iré actualizando este proyecto y también este README con los pasos necesarios para ejecutar el proyecto. 
