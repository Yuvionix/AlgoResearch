type PageProps = {
  kicker: string;
  title: string;
  lede: string;
  children: React.ReactNode;
};

export default function Page({ kicker, title, lede, children }: PageProps) {
  return (
    <div className="page">
      <p className="kicker">{kicker}</p>
      <h1>{title}</h1>
      <p className="lede">{lede}</p>
      {children}
    </div>
  );
}