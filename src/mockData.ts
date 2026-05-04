import type { Action, Feedback, Suggestion } from "./types/api";
import type { Routine } from "./api/routines";

export const mockBrainDump =
  "프로젝트 발표 준비해야 하는데 자료도 정리해야 하고 교수님께 질문 메일도 보내야 하고 팀원에게 일정도 공유해야 함";

export const mockSuggestions: Suggestion[] = [
  {
    id: 101,
    session_id: 22,
    brain_dump_id: 8,
    parent_suggestion_id: null,
    generation_type: "original",
    source: "rule_based",
    title: "발표 자료 제목 작성",
    micro_step: "첫 번째 슬라이드 제목만 적기",
    effort_level: "quiet",
    created_at: "today 14:20",
  },
  {
    id: 102,
    session_id: 22,
    brain_dump_id: 8,
    parent_suggestion_id: null,
    generation_type: "original",
    source: "ai",
    title: "교수님 메일 초안",
    micro_step: "교수님께 보낼 질문 메일 첫 줄만 쓰기",
    effort_level: "gentle",
    created_at: "today 14:20",
  },
  {
    id: 103,
    session_id: 22,
    brain_dump_id: 8,
    parent_suggestion_id: null,
    generation_type: "original",
    source: "rule_based",
    title: "팀 일정 공유",
    micro_step: "팀원에게 일정 공유 메시지 초안 한 줄 쓰기",
    effort_level: "neutral",
    created_at: "today 14:20",
  },
];

export const mockSmallerSuggestions: Suggestion[] = [
  {
    id: 201,
    session_id: 22,
    brain_dump_id: 8,
    parent_suggestion_id: 102,
    generation_type: "smaller",
    source: "rule_based",
    title: "메일 창만 열기",
    micro_step: "메일 작성 창만 열기",
    effort_level: "quiet",
    created_at: "today 14:22",
  },
  {
    id: 202,
    session_id: 22,
    brain_dump_id: 8,
    parent_suggestion_id: 102,
    generation_type: "smaller",
    source: "rule_based",
    title: "받는 사람 입력",
    micro_step: "받는 사람 칸에 교수님 주소만 입력하기",
    effort_level: "quiet",
    created_at: "today 14:22",
  },
];

export const mockActiveAction: Action = {
  id: 33,
  session_id: 22,
  suggestion_id: 102,
  title: "교수님 메일 초안",
  micro_step: "교수님께 보낼 질문 메일 첫 줄만 쓰기",
  status: "active",
  completion_note: null,
  abort_reason: null,
  created_at: "today 14:23",
  updated_at: "today 14:23",
};

export const mockFeedback: Feedback[] = [
  {
    id: 1,
    session_id: 22,
    suggestion_id: 102,
    action_id: 33,
    reaction: "do",
    note: null,
    created_at: "today 14:23",
  },
  {
    id: 2,
    session_id: 22,
    suggestion_id: 103,
    action_id: null,
    reaction: "make_smaller",
    note: "크기를 줄이는 신호",
    created_at: "today 14:24",
  },
  {
    id: 3,
    session_id: 21,
    suggestion_id: 95,
    action_id: null,
    reaction: "capture_only",
    note: "기록만 저장",
    created_at: "yesterday",
  },
];

export const mockHistoryRows = [
  ["Brain Dump", "5 candidates", "today 14:20", "completed 1"],
  ["make_smaller", "3 smaller", "today 11:04", "aborted"],
  ["Action completed", "메일 첫 줄", "yesterday", "done"],
  ["capture_only", "기록만 저장", "yesterday", "no action"],
  ["Routine", "책상 3개 정리", "monday", "completed"],
];

export const mockRoutines: Routine[] = [
  {
    id: 1,
    title: "물 한 컵 마시기",
    micro_step: "컵에 물을 따르고 한 모금 마시기",
    mode: "quiet",
    enabled: true,
  },
  {
    id: 2,
    title: "책상 위 3개 정리",
    micro_step: "눈앞에 보이는 물건 3개만 제자리로 옮기기",
    mode: "gentle",
    enabled: true,
  },
  {
    id: 3,
    title: "메일 제목만 쓰기",
    micro_step: "메일 작성 창을 열고 제목 한 줄만 적기",
    mode: "neutral",
    enabled: false,
  },
];
