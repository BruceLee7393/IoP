<template>
  <router-view />
</template>

<style>
/* Element Plus弹出层层级修复 */
.el-popper {
  z-index: 9999 !important;
}

/* 确保下拉菜单在移动端正确显示 */
.el-dropdown-menu {
  z-index: 9999 !important;
}
</style>
