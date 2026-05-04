export interface Routine {
  id: number;
  title: string;
  micro_step: string;
  mode: "quiet" | "gentle" | "neutral";
  enabled: boolean;
}

export const routineSeeds: Routine[] = [
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
    micro_step: "눈앞의 물건 3개만 제자리로 옮기기",
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
