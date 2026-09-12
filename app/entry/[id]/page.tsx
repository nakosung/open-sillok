import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {ArrowLeft,ArrowRight} from "lucide-react";
import {entries,entryDate} from "@/lib/annals";
import {SiteHeader} from "@/components/site-header";
import {EntryReader} from "@/components/entry-reader";

type Props={params:Promise<{id:string}>};
export async function generateMetadata({params}:Props):Promise<Metadata>{
  const {id}=await params;const e=entries.find(e=>e.id===id);
  if(!e)return {title:"Entry not found",robots:{index:false,follow:false}};
  return {title:e.title,description:`${e.king}, ${entryDate(e)}, ${e.year}. A new AI draft translation with the complete original Classical Chinese text.`,alternates:{canonical:`/entry/${e.id}`}};
}
export default async function EntryPage({params}:Props){
  const {id}=await params;const index=entries.findIndex(e=>e.id===id);if(index<0)notFound();const e=entries[index];
  return <><a href="#entry-main" className="skip-link">Skip to entry</a><SiteHeader/><main id="entry-main" className="standalone-main"><Link className="back-link" href={`/?entry=${e.id}`}><ArrowLeft size={16}/>Back to reading room</Link><EntryReader entry={e} standalone/><nav className="related-entries" aria-label="Adjacent entries">{index>0?<Link href={`/entry/${entries[index-1].id}`}><ArrowLeft size={14}/> Previous entry</Link>:<span/>}{index<entries.length-1&&<Link href={`/entry/${entries[index+1].id}`}>Next entry <ArrowRight size={14}/></Link>}</nav></main></>;
}
