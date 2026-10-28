// UI strings live in src/i18n/<lang>.json so a Hindi version can be added later.
import en from "../i18n/en.json";
const dict = { en };
export const t = (key, lang = "en") => key.split(".").reduce((o, k) => o?.[k], dict[lang]) ?? key;
