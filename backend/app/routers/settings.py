# routers/settings.py — LLM 配置（模式查询 / 保存 / 缓存状态）

from fastapi import APIRouter

from app.schemas import SettingsIn
from core.config import get_mode_label, load_settings, save_settings

router = APIRouter()


@router.get("/status")
def status():
    """当前 LLM 模式（前端顶栏角标用）。Key 永远不回传明文。"""
    label, mode = get_mode_label()
    s = load_settings()
    key = s.get("api_key", "")
    masked = (key[:6] + "..." + key[-4:]) if key and len(key) > 12 else ("已设置" if key else "")
    return {
        "mode": mode,
        "mode_label": label,
        "provider": s.get("provider", ""),
        "base_url": s.get("base_url", ""),
        "model": s.get("model", ""),
        "api_key_masked": masked,
    }


@router.post("/save")
def save(req: SettingsIn):
    """保存 LLM 配置（api_key 落盘前自动 AES-GCM 加密）。"""
    save_settings(req.provider, req.api_key, req.base_url, req.model)
    return {"ok": True}


@router.get("/cache")
def cache_status():
    """缓存与限流状态（设置面板用）。"""
    from tools.cache_store import cache_stats
    from tools.rate_limiter import status as rate_status

    try:
        cache = cache_stats()
    except Exception:
        cache = {}
    return {"cache": cache, "rate_limiter": rate_status()}


@router.post("/cache/clear")
def cache_clear():
    """清空结果缓存。"""
    from tools.cache_store import clear_cache

    try:
        clear_cache()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
