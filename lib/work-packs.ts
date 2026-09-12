import prepared from "@/data/work-packs.json";
import guide from "@/data/contribution-guide.json";
export type WorkPack={schemaVersion:number;id:string;kind:string;targetPath:string;source:{sourceUrl:string;original:string;originalSha256:string;[key:string]:unknown};translation:unknown};
const packs=prepared as Record<string,WorkPack>;
export const getWorkPack=(id:string)=>Object.hasOwn(packs,id)?{...packs[id],instructions:guide.instructions,submission:"Save only the translation object at targetPath. Fill your contributor handle, actual model, dates and method; preserve earlier credit. A download does not reserve the task."}:undefined;
