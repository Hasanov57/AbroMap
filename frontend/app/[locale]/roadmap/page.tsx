import { Suspense } from "react";
import { Roadmap } from "@/components/roadmap";
export default function RoadmapPage() {
  return (
    <Suspense>
      <Roadmap />
    </Suspense>
  );
}
