// Server-side repository. Reader clients receive one page of metadata and one entry.
import corpus from "@/data/entries.json";
import type {Entry,CatalogEntry,SearchResult} from "./entry";
export {edition,sourceUrl,entryDate,citation} from "./entry";
export type {Entry} from "./entry";
export const entries=corpus as Entry[];
export const getEntry=(id:string)=>entries.find(e=>e.id===id);
export const searchEntries=(query:string,king="all",topic="all")=>{
  const words=query.normalize("NFKC").toLowerCase().trim().split(/\s+/).filter(Boolean);
  return entries.filter(e=>(king==="all"||e.king===king)&&(topic==="all"||e.topics.includes(topic))&&words.every(q=>`${e.title} ${e.king} ${e.kingKo} ${e.year} ${e.topics.join(" ")} ${(e.keywords??[]).join(" ")} ${e.original} ${e.translation.join(" ")} ${e.id}`.normalize("NFKC").toLowerCase().includes(q)));
};
export const toCatalog=(e:Entry):CatalogEntry=>({id:e.id,title:e.title,king:e.king,year:e.year,month:e.month,day:e.day,leapMonth:e.leapMonth,dateScope:e.dateScope,topics:e.topics,reviewStatus:e.reviewStatus});
export const catalogSearch=(query:string,king="all",topic="all",offset=0,limit=30):SearchResult=>{
  const matches=searchEntries(query,king,topic);return {items:matches.slice(offset,offset+limit).map(toCatalog),total:matches.length,offset,limit,nextOffset:offset+limit<matches.length?offset+limit:null};
};
export const catalogOptions={kings:[...new Set(entries.map(e=>e.king))],topics:[...new Set(entries.flatMap(e=>e.topics))].sort()};
