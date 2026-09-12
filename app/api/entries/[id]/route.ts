import {getEntry} from "@/lib/annals";
export async function GET(_request:Request,{params}:{params:Promise<{id:string}>}){
  const {id}=await params;const entry=getEntry(id);
  if(!entry)return Response.json({error:"Entry not found"},{status:404});
  return Response.json(entry,{headers:{"Cache-Control":"public, max-age=300","X-Content-Type-Options":"nosniff"}});
}
