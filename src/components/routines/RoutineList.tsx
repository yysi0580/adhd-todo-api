import { mockRoutines } from "../../mockData";
import { RoutineCard } from "./RoutineCard";

export function RoutineList() {
  return (
    <div className="grid grid-cols-3 gap-4">
      {mockRoutines.map((routine) => (
        <RoutineCard key={routine.id} routine={routine} />
      ))}
    </div>
  );
}
