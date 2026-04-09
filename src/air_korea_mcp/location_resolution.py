from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Set

from .constants import VALID_SIDO_NAME_OPTIONS
from .exceptions import AirKoreaError
from .location_index_data import LOWER_LEVEL_REGION_INDEX

SIDO_ALIAS_MAP: Dict[str, str] = {
    "서울": "서울",
    "서울특별시": "서울",
    "서울시": "서울",
    "부산": "부산",
    "부산광역시": "부산",
    "부산시": "부산",
    "대구": "대구",
    "대구광역시": "대구",
    "대구시": "대구",
    "인천": "인천",
    "인천광역시": "인천",
    "인천시": "인천",
    "광주": "광주",
    "광주광역시": "광주",
    "광주시": "광주",
    "대전": "대전",
    "대전광역시": "대전",
    "대전시": "대전",
    "울산": "울산",
    "울산광역시": "울산",
    "울산시": "울산",
    "세종": "세종",
    "세종특별자치시": "세종",
    "경기": "경기",
    "경기도": "경기",
    "강원": "강원",
    "강원도": "강원",
    "강원특별자치도": "강원",
    "충북": "충북",
    "충청북도": "충북",
    "충남": "충남",
    "충청남도": "충남",
    "전북": "전북",
    "전라북도": "전북",
    "전북특별자치도": "전북",
    "전남": "전남",
    "전라남도": "전남",
    "경북": "경북",
    "경상북도": "경북",
    "경남": "경남",
    "경상남도": "경남",
    "제주": "제주",
    "제주도": "제주",
    "제주특별자치도": "제주",
    "전국": "전국",
}


def resolve_sido_name(location_name: str) -> str:
    normalized = normalize_location_name(location_name)

    direct = SIDO_ALIAS_MAP.get(normalized)
    if direct is not None:
        return direct

    prefixed = resolve_sido_from_prefix(normalized)
    if prefixed is not None:
        return prefixed

    exact_candidates = LOWER_LEVEL_REGION_INDEX.get(normalized)
    if exact_candidates:
        return resolve_candidate_list(location_name=normalized, candidates=exact_candidates)

    token_candidates = collect_token_candidates(normalized.split())
    if token_candidates:
        shared_candidates = intersect_candidates(token_candidates)
        if shared_candidates:
            return resolve_candidate_list(location_name=normalized, candidates=shared_candidates)

        merged_candidates = sorted({candidate for candidates in token_candidates for candidate in candidates})
        return resolve_candidate_list(location_name=normalized, candidates=merged_candidates)

    allowed = ", ".join(VALID_SIDO_NAME_OPTIONS)
    raise AirKoreaError(
        "sido_name must be a valid 시도 name or a uniquely resolvable lower-level location. "
        f"Known top-level values: {allowed}"
    )


def normalize_location_name(value: str) -> str:
    return " ".join(value.strip().split())


def resolve_sido_from_prefix(location_name: str) -> str | None:
    for alias, sido in sorted(SIDO_ALIAS_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        if location_name.startswith(f"{alias} "):
            return sido
    return None


def collect_token_candidates(tokens: Sequence[str]) -> List[List[str]]:
    token_candidates: List[List[str]] = []
    for token in tokens:
        direct = SIDO_ALIAS_MAP.get(token)
        if direct is not None:
            return [[direct]]

        candidates = LOWER_LEVEL_REGION_INDEX.get(token)
        if candidates:
            token_candidates.append(candidates)
    return token_candidates


def intersect_candidates(candidate_lists: Iterable[Sequence[str]]) -> List[str]:
    iterator = iter(candidate_lists)
    try:
        shared: Set[str] = set(next(iterator))
    except StopIteration:
        return []

    for candidates in iterator:
        shared.intersection_update(candidates)
    return sorted(shared)


def resolve_candidate_list(location_name: str, candidates: Sequence[str]) -> str:
    unique_candidates = sorted(set(candidates))
    if len(unique_candidates) == 1:
        return unique_candidates[0]

    candidate_text = ", ".join(unique_candidates)
    raise AirKoreaError(
        f"sido_name '{location_name}' is ambiguous. Use one of these top-level regions explicitly: {candidate_text}"
    )
