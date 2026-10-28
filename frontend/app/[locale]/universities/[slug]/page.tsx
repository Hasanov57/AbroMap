import { UniversityDetail } from "@/components/university-detail";
export default async function UniversityPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return <UniversityDetail slug={slug} />;
}
