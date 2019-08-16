--
-- Name: getsequenceorthologsequence(integer, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getsequenceorthologsequence(integer, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      queryCursor refcursor;
      myOrth integer;
      querySequence ALIAS for $1;
      injectionBlastSearch ALIAS for $2;
   BEGIN   
      myOrth := null;

      open queryCursor for 
      select
         dbo.hitsequence
      from    
         databasesearchobservation dbo where
         dbo.databasesearchstudy = injectionBlastSearch and
         dbo.querysequence = querySequence and
         dbo.userflags like  '%Ortholog%';

      fetch queryCursor into myOrth;
     
      if not found then
         close queryCursor;
         open queryCursor for 
         select
            dbo.querysequence
         from    
            databasesearchobservation dbo where
            dbo.databasesearchstudy = injectionBlastSearch and
            dbo.hitsequence = querySequence and
            dbo.userflags like  '%Ortholog%';

         fetch queryCursor into myOrth;

      end if;

      close queryCursor;

      return myOrth;
   END;
$_$;


ALTER FUNCTION public.getsequenceorthologsequence(integer, integer) OWNER TO agrbrdf;

