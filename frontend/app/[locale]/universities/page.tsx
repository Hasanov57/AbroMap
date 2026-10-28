import { Suspense } from "react";
import { UniversityDirectory } from "@/components/university-directory";
export default function Universities() {
  return (
    <Suspense>
      <UniversityDirectory />
    </Suspense>
  );
}
