<template>
  <div class="page-container">
    <div class="content-wrapper">
      <div class="banner" ref="banner">
        欢迎使用倍量科技产品管理系统
      </div>

      <div class="home-container" ref="homeContainer">
        <img src="@/assets/images/1.png" alt="首页图" class="logo"
             ref="logo" @load="onLogoLoad" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const logo = ref(null);
const homeContainer = ref(null);
const banner = ref(null);


</script>


<style scoped>
.page-container {
  width: 100%;
  height: calc(100vh - var(--header-height));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
}

.banner {
  flex-shrink: 0;
  width: 100%;
  padding:12px 0px;
  text-align: center;
  color: #004085;
  font-size: 40px;
  font-weight: bold;
}

.home-container { display: flex; align-items: center; width: 100%; overflow: hidden; }

</style>
