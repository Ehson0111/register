<!--
  AboutView — заглушка из шаблона Vue (в router не подключена)
  Полезна как пример минимального SFC: только template + style, без script
-->
<template>
  <div class="about">
    <h1>This is an about page</h1>
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>
