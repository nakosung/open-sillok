import {ReadingRoom} from "@/components/reading-room";
import {catalogSearch,catalogOptions,searchEntries,entries} from "@/lib/annals";
type Params=Record<string,string|string[]|undefined>;
export default async function Home({searchParams}:{searchParams:Promise<Params>}){
  const p=await searchParams;const value=(k:string)=>typeof p[k]==="string"?p[k] as string:"";
  const q=value("q").slice(0,300),king=catalogOptions.kings.includes(value("king"))?value("king"):"all",topic=catalogOptions.topics.includes(value("topic"))?value("topic"):"all";
  const matches=searchEntries(q,king,topic);const selected=matches.find(e=>e.id===value("entry"))??matches[0]??null;
  return <ReadingRoom initialResult={catalogSearch(q,king,topic)} initialEntry={selected} initialFilters={{q,king,topic,open:!!value("entry")}} options={catalogOptions} editionCount={entries.length}/>;
}
