--
-- Name: annotatereciprocaltophits2(integer, integer, boolean, boolean); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION annotatereciprocaltophits2(integer, integer, boolean, boolean) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      querycursor refcursor;
      blastsearch1 ALIAS for $1;
      blastsearch2 ALIAS for $2;
      annotateSearch1 ALIAS for $3;
      annotateSearch2 ALIAS for $4;
      tophit int4;
      tophitstophit int4;
      currentquery int4;
      reciprocalcount int4;
   BEGIN   
      --the annotateSearch* parms control which of the two searches we are to flag - usually
      -- you would only flag the queries in the first search
      if not annotateSearch1 and not annotateSearch2 then
         return 0;
      end if;
      
      open querycursor for
    select distinct
          querysequence
        from 
           databasesearchobservation 
        where
           databasesearchstudy = blastsearch1;

      fetch querycursor into currentquery;
      reciprocalcount := 0;

      while found LOOP
      
         -- get the top hit of this query
         tophit := getTopSearchHit(currentquery, blastsearch1);

         -- if the top hit of the top hit is the current query, annotate
         -- reciprocal
         if tophit is not null then
            tophitstophit := getTopSearchHit(tophit,blastsearch2);
            if tophitstophit = currentquery then
               if annotateSearch1 then
                  update databasesearchobservation
                  set userflags = coalesce(userflags || ',Reciprocal Top Hit', 'Reciprocal Top Hit'),
                  lastupdateddate = now()
                  where databasesearchstudy = blastsearch1 and 
                  querysequence = currentquery and
                  hitsequence = tophit;
               end if;

               if annotateSearch2 then
                  update databasesearchobservation
                  set userflags = coalesce(userflags || ',Reciprocal Top Hit', 'Reciprocal Top Hit'),
                  lastupdateddate = now()
                  where databasesearchstudy = blastsearch2 and 
                  querysequence = tophit and
                  hitsequence = currentquery;
               end if;

               reciprocalcount := reciprocalcount + 1;
            end if;
         end if;

         fetch querycursor into currentquery;

      end LOOP;


      close querycursor;
      return reciprocalcount;
    END;
$_$;


ALTER FUNCTION public.annotatereciprocaltophits2(integer, integer, boolean, boolean) OWNER TO agrbrdf;

