--
-- Name: installcontributedtable(character varying, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION installcontributedtable(character varying, character varying, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
declare
   contribtablename alias for $1;
   displaytext alias for $2;
   descriptiontext alias for $3;

   sqlcode varchar;
   typeid integer;
   maxtypeid integer;
   mintypeid integer;
   junk integer;
   rec record;
   mycount integer;
   msg varchar;
   installquery refcursor;
   newobid integer;
BEGIN
   mintypeid = 10000;
   maxtypeid = 100000;


   -- try selecting datasourceob and voptypeid from the 
   -- table to check its been done properly - if not add these columns
   sqlcode := 'select datasourceob , voptypeid from ' || contribtablename;

   begin
      for rec in EXECUTE sqlcode LOOP 
         exit;
      end loop;
   exception
      when others then
      sqlcode = 'alter table ' || contribtablename || ' add datasourceob integer';
      EXECUTE sqlcode;
      sqlcode = 'alter table ' || contribtablename || ' add voptypeid integer';
      EXECUTE sqlcode;

      -- used to just fail it
      --raise exception 'Failed executing check query %' , sqlcode;
   end;

   -- now check that this table has not already been installed. It is not necessarily an error to install 
   -- a table more than once- however it should certainly not have identical display and description names
   select count(*) into mycount from obtype where upper(tablename) = upper(contribtablename)
          and upper(displayname) = upper(displaytext) 
          and upper(obtypedescription) = upper(descriptiontext);

   if mycount > 0 then
      raise exception 'A table with this name and identical description and displayname is already installed';
   end if;
   
 
   -- obtain the next typeid that we can use for this fact dimension. By convention all the contributed
   -- fact tables have a typeid are > 10000
   typeid := mintypeid;
   while typeid < 100000 loop
      select obtypeid into junk from obtype where obtypeid = typeid;
      exit when not FOUND;
      typeid := typeid + 1;
   end loop;

   if typeid > 100000 then
      raise exception 'Unable to obtain a data dimension typeid within range';
   end if;


   -- check to see whether there is an existing data source to use - if not set up the data source
   newobid := null;
   select obid into newobid from datasourceob where xreflsid = 'Contributed Table.'||contribtablename;
   if newobid is null then

      -- set up the new data source
      select nextval('ob_obidseq') into newobid;

      insert into datasourceob (
         obid,
         xreflsid,
         datasourcename,
         datasourcetype,
         datasourcecomment)
      values (
         newobid,
         'Contributed Table.'||contribtablename,
         displaytext,
         'Contributed Database Table',
         descriptiontext
      );
   end if;



   -- set up the new dimension 
   insert into obtype (obtypeid , displayname, tablename, namedinstances, obtypedescription,isop,isvirtual)
   values(typeid, displaytext,contribtablename,FALSE,descriptiontext,TRUE,TRUE);

   insert into optypesignature (   obtypeid , argobtypeid , optablecolumn )
   select typeid,   obtypeid,   'datasourceob' from obtype where  upper(tablename) = 'DATASOURCEOB';

   sqlcode := 'update ' || contribtablename || 
              ' set datasourceob = ' || to_char(newobid,'999999999')||
               ',voptypeid = ' || to_char(typeid,'9999999') ||
               ' where datasourceob is null';
   EXECUTE sqlcode;


   -- create a required index, replacing any dots in the index name (e.g. if installing a table in another schema)
   sqlcode = 'create index isystem_' || replace(contribtablename,'.','_') || ' on ' || contribtablename || '(datasourceob, voptypeid)';
   EXECUTE sqlcode;

   return typeid;
END;
$_$;


ALTER FUNCTION public.installcontributedtable(character varying, character varying, character varying) OWNER TO agrbrdf;

