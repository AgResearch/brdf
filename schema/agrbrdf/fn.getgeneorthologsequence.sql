--
-- Name: getgeneorthologsequence(integer, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getgeneorthologsequence(integer, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      queryCursor refcursor;
      myOrth integer;
      queryGene ALIAS for $1;
      injectionBlastSearch ALIAS for $2;
   BEGIN   
      myOrth := null;

      open queryCursor for 
      select
         dbo.hitsequence
      from
         ((geneticob g join geneproductlink gpl on
         gpl.geneticob = g.obid)  join
         databasesearchobservation dbo on
         dbo.databasesearchstudy = injectionBlastSearch and
         dbo.querysequence = gpl.biosequenceob and
         dbo.userflags like  '%Ortholog%') 
      where
         g.obid = queryGene;

      fetch queryCursor into myOrth;

      if not found then
         close queryCursor;

         open queryCursor for 
         select
            dbo.querysequence
         from
            ((geneticob g join geneproductlink gpl on
            gpl.geneticob = g.obid)  join
            databasesearchobservation dbo on
            dbo.databasesearchstudy = injectionBlastSearch and
            dbo.hitsequence = gpl.biosequenceob and
            dbo.userflags like  '%Ortholog%') 
         where
            g.obid = queryGene;

         fetch queryCursor into myOrth;

      end if;


      close queryCursor;

      return myOrth;

   END;
$_$;


ALTER FUNCTION public.getgeneorthologsequence(integer, integer) OWNER TO agrbrdf;

