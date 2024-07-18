function updateColorScheme() {
  function scheme(hour){
    if (hour >= 5 && hour < 12) return "morning";
    if (hour >= 12 && hour < 17) return "day";
    if (hour >= 17 && hour < 21) return "evening";
    return "night";
  };

  const hour = new Date().getHours();
  document.body.className = scheme(hour);
}
