import { ProgramDetail } from "@/components/program-detail";
export default async function ProgramPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ProgramDetail id={Number(id)} />;
}
