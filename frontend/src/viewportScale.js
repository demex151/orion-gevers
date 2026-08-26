function applyGeverScale() {
  const designWidth = 1440;
  const designHeight = 1024;
  const scale = Math.min(
    1,
    window.innerWidth / designWidth,
    window.innerHeight / designHeight,
  );

  document.documentElement.style.setProperty(
    "--gever-scale",
    String(scale),
  );
}

applyGeverScale();
window.addEventListener("resize", applyGeverScale);
window.addEventListener("orientationchange", applyGeverScale);

export default applyGeverScale;
