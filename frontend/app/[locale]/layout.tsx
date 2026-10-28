import type { Metadata } from "next";
import { NextIntlClientProvider, hasLocale } from "next-intl";
import { getMessages } from "next-intl/server";
import { notFound } from "next/navigation";
import { routing } from "@/i18n/routing";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import "../globals.css";

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}
export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const copy = {
    az: [
      "AbroMap — Xaricdə təhsilə gedən yolun xəritəsi",
      "Universitetləri və təqaüdləri şəffaf uyğunluq qiymətləndirməsi ilə kəşf edin.",
    ],
    en: [
      "AbroMap — Your roadmap to studying abroad",
      "Discover study abroad programs with transparent matching and sourced requirements.",
    ],
    ru: [
      "AbroMap — Ваш маршрут к учёбе за рубежом",
      "Находите зарубежные программы с прозрачной оценкой соответствия и ссылками на источники.",
    ],
  } as const;
  const [title, description] = copy[locale as keyof typeof copy] || copy.az;
  return { title, description };
}
export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) notFound();
  const messages = await getMessages();
  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider messages={messages}>
          <Header />
          <main>{children}</main>
          <Footer />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
