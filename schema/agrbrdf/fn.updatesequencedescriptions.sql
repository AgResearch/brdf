--
-- Name: updatesequencedescriptions(character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION updatesequencedescriptions(character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
declare
   updatecursor refcursor;
   prefix alias for $1;
   updatehit varchar;
   updatedescription varchar;
   updatecount int4;
begin
   updatecount := 0;
   open updatecursor for 
      select accession, replace(description,'"','') 
      from scratch;

   fetch updatecursor into updatehit,updatedescription;
   while FOUND loop
      update biosequenceob set 
      sequencedescription = updatedescription,
      lastupdateddate = now()
      where sequencename = updatehit and
      xreflsid = prefix || '.' || updatehit;
      fetch updatecursor into updatehit,updatedescription;
      updatecount := updatecount + 1;
   end loop;

   --commit;

   close updatecursor;

   return updatecount;

end;
$_$;


ALTER FUNCTION public.updatesequencedescriptions(character varying) OWNER TO agrbrdf;

