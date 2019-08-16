--
-- Name: annotatereciprocaltophits(integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION annotatereciprocaltophits(integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      querycursor refcursor;
      blastsearch ALIAS for $1;
      tophit int4;
      tophitstopquery int4;
      currentquery int4;
      reciprocalcount int4;
   BEGIN   
      
      open querycursor for
    select distinct
          querysequence
        from 
           databasesearchobservation 
        where
           databasesearchstudy = blastsearch;

      fetch querycursor into currentquery;
      reciprocalcount := 0;

      while found LOOP
      
         -- get the top hit of this query
         tophit := getTopSearchHit(currentquery, blastsearch);

         -- if the top query of the top hit is the current query, annotate
         -- reciprocal
         if tophit is not null then
            tophitstopquery := getTopSearchQuery(tophit,blastsearch);
            if tophitstopquery = currentquery then
               update databasesearchobservation
               set userflags = coalesce(userflags || ',Reciprocal Top Hit(1)', 'Reciprocal Top Hit(1)'),
               lastupdateddate = now()
               where databasesearchstudy = blastsearch and 
               querysequence = currentquery and
               hitsequence = tophit;
               reciprocalcount := reciprocalcount + 1;
            end if;
         end if;

         fetch querycursor into currentquery;

      end LOOP;


      close querycursor;
      return reciprocalcount;
    END;
$_$;


ALTER FUNCTION public.annotatereciprocaltophits(integer) OWNER TO agrbrdf;

--
-- Name: annotatereciprocaltophits(integer, integer, integer, boolean, boolean); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION annotatereciprocaltophits(integer, integer, integer, boolean, boolean) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
-- this use the method of
-- Proc. Natl. Acad. Sci. USA
--Vol. 95, pp. 6239-6244, May 1998
--Genetics
--Genomic evidence for two functionally distinct gene classes
--MARIA C. RIVERA, RAVI JAIN, JONATHAN E. MOORE, AND JAMES A. LAKE* 
-- ...orthologs were selected according to a symmetrical (distancelike)
--procedure by using MSPs. If a and b are orthologous
--genes in genomes A and B, respectively, then we required that
--a BLASTP search of database B with gene a should select gene
--b and the reciprocal search of database A with gene b should
--select gene a. The four sequences with the highest MSPs were
--selected from each BLASTP comparison, and from this 4 * 4
--array of scores, sij, reciprocal pairs were selected (if any
--existed). The best pair, corresponding to the minimum value
--of i + j and the maximum sum of scores, was then chosen as
--the ortholog pair.
   DECLARE
      querycursor refcursor;
      searchcursor refcursor;
      search2cursor refcursor;
      searchrecord record;
      blastsearch1 ALIAS for $1;
      blastsearch2 ALIAS for $2;
      depth ALIAS for $3;
      annotateSearch1 ALIAS for $4;
      annotateSearch2 ALIAS for $5;
      currentquery integer;
      lasthit integer;
      hitcount integer;
      querycount integer;

      forwardmspids integer[];
      forwardmspscores float[];
      forwardmspevalues float[];
      forwardmspids_l integer;

      reversemspids integer[];
      reversemspscores float[];
      reversemspevalues float[];
      reversemspids_l integer;

      minfindex integer[];
      minfindex_l integer;
      minrindex integer[];

      reciprocalindex integer;

      i integer;
      j integer;
      ijmin integer;
      scoremax float;
      reciprocalcount integer;

      
     
 
   BEGIN   
      -- master query to loop through all seqs to be considered
      open querycursor for
    	select distinct
       	   querysequence
        from 
           databasesearchobservation 
        where
           databasesearchstudy = blastsearch1;

      fetch querycursor into currentquery;

      querycount := 0;
      reciprocalcount := 0;
      while found  LOOP
         hitcount := 0;
         lasthit := 0;
         forwardmspids_l := 0;
         reversemspids_l := 0;
         querycount := querycount + 1;
    
      
         -- get the top "depth" hits of this query
         open searchcursor for 
    	 select
       	    dso.hitsequence,
            dso.hitevalue,
            saf.score
         from 
            databasesearchobservation dso left outer join sequencealignmentfact saf on
            saf.databasesearchobservation = dso.obid
         where           
            dso.databasesearchstudy = blastsearch1 and 
            dso.querysequence = currentquery 
         order by
            dso.hitevalue asc,
            saf.score desc;

         fetch searchcursor into searchrecord;

         while found and hitcount < depth loop

            if lasthit != searchrecord.hitsequence then
               hitcount := hitcount + 1;
               forwardmspids[hitcount] := searchrecord.hitsequence;
               forwardmspscores[hitcount] := searchrecord.score;
               forwardmspevalues[hitcount] := searchrecord.hitevalue;
               forwardmspids_l := forwardmspids_l + 1;
               lasthit := searchrecord.hitsequence;
            end if;

            fetch searchcursor into searchrecord;

         end loop;

         close searchcursor;
         --perform mylog(1,'forward='||to_char(hitcount,'99999'));


         -- get the top "depth" seqs that hit this query 
         hitcount := 0;
         lasthit := 0;

         open searchcursor for
         select
            dso.querysequence,
            dso.hitevalue,
            saf.score
         from
            databasesearchobservation dso left outer join sequencealignmentfact saf on
            saf.databasesearchobservation = dso.obid
         where
            dso.databasesearchstudy = blastsearch2 and
            dso.hitsequence = currentquery
         order by
            dso.hitevalue asc,
            saf.score desc;

         fetch searchcursor into searchrecord;

         while found and hitcount < depth loop

            if lasthit != searchrecord.querysequence then
               hitcount := hitcount + 1;
               reversemspids[hitcount] := searchrecord.querysequence;
               reversemspscores[hitcount] := searchrecord.score;
               reversemspevalues[hitcount] := searchrecord.hitevalue;
               reversemspids_l := reversemspids_l + 1;
               lasthit := searchrecord.querysequence;
            end if;

            fetch searchcursor into searchrecord;

         end loop;

         close searchcursor;
         --perform mylog(1,'reverse='||to_char(hitcount,'99999'));

         -- attempt to find the best reciprocal hit. Best is that with minimum
         -- of (i+j) , and then for same i+j, minimum of sum of scores 
         -- first create an array containing all candidates that have the same
         -- minimum i+j - we store the index of each candidate in the forward array

         ijmin := 1 + forwardmspids_l + reversemspids_l;
         minfindex_l := 0;
         for i in 1..forwardmspids_l loop
            for j in 1..reversemspids_l loop
               if (i + j < ijmin) and forwardmspids[i] = reversemspids[j] then
                  minfindex_l := minfindex_l + 1;
                  minfindex[minfindex_l] := i;
                  minrindex[minfindex_l] := j;
                  ijmin := i + j;
               end if;
            end loop;
         end loop;
         --perform mylog(2,'minfindex_l='||to_char(minfindex_l,'99999'));


         -- find the candidate with the minimum sum of score
         reciprocalindex := 0;
         scoremax := 0;
         for i in 1..minfindex_l loop
            --perform mylog(1,'comparing '||to_char(forwardmspscores[minfindex[i]],'99999') || ' ' || to_char(reversemspscores[minfindex[i]],'99999'));
            if (forwardmspscores[minfindex[i]] + reversemspscores[minrindex[i]]) > scoremax then
               reciprocalindex := i;
               scoremax := forwardmspscores[minfindex[i]] + reversemspscores[minrindex[i]];
            end if;
         end loop;

         -- annotate if we have one
         if reciprocalindex != 0 then

            if annotateSearch1 then
               update databasesearchobservation
               set userflags = coalesce(userflags || ',Best Reciprocal Hit', 'Best Reciprocal Hit'),
               lastupdateddate = now()
               where databasesearchstudy = blastsearch1 and 
               querysequence = currentquery and
               hitsequence = forwardmspids[minfindex[reciprocalindex]];
            end if;

            if annotateSearch2 then
               update databasesearchobservation
               set userflags = coalesce(userflags || ',Best Reciprocal Hit', 'Best Reciprocal Hit'),
               lastupdateddate = now()
               where databasesearchstudy = blastsearch2 and
               hitsequence = currentquery  and
               querysequence = forwardmspids[minfindex[reciprocalindex]];
            end if;

            reciprocalcount := reciprocalcount + 1;
         end if;

         fetch querycursor into currentquery;
   
      end LOOP;

      close querycursor;

      return reciprocalcount;

    END;
$_$;


ALTER FUNCTION public.annotatereciprocaltophits(integer, integer, integer, boolean, boolean) OWNER TO agrbrdf;

