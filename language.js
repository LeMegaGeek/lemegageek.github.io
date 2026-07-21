(function () {
  "use strict";

  var params = new URLSearchParams(window.location.search);
  var requested = params.get("lang");
  var stored = null;

  try {
    if (requested === "en" || requested === "fr") {
      window.localStorage.setItem("lemegageek-language", requested);
      stored = requested;
    } else {
      stored = window.localStorage.getItem("lemegageek-language");
    }
  } catch (_error) {
    stored = requested;
  }

  var browserLanguage = (navigator.languages && navigator.languages[0]) || navigator.language || "en";
  var preferred = stored || (browserLanguage.toLowerCase().startsWith("fr") ? "fr" : "en");
  var pageLanguage = document.documentElement.lang;

  if (pageLanguage === "en" && preferred === "fr") {
    window.location.replace("/fr/?lang=fr");
  } else if (pageLanguage === "fr" && preferred === "en") {
    window.location.replace("/?lang=en");
  }
})();
