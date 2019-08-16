--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: agrbrdf
--

CREATE OR REPLACE PROCEDURAL LANGUAGE plpgsql;


ALTER PROCEDURAL LANGUAGE plpgsql OWNER TO agrbrdf;

SET search_path = public, pg_catalog;

--
-- Name: addcomment(integer, text, text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION addcomment(integer, text, text) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   declare 
      commenton alias for $1;
      commenttext alias for $2;
      author alias for $3;
      mycur refcursor;
      existingcomment integer;
      commentonlsid varchar(2048);
      junk integer;
   begin

      /* get the lsid of the commented object */
      select xreflsid||':comment' into commentonlsid from ob where obid = commenton;


      /* check if we can re-use a comment */
      existingcomment := null;
      open mycur for 
      select obid from commentob where commentstring = commenttext;
      fetch mycur into existingcomment;
      close mycur;

      if existingcomment is null then
         existingcomment := getNewObid();
         insert into commentob(obid, xreflsid, commentstring)
         values (existingcomment, commentonlsid, commenttext);
      end if;

      /* check if this object already commented with this comment */
      select ob into junk from commentlink where commentob = existingcomment and ob = commenton;
      if not FOUND then
         insert into commentlink(ob,commentob,commentby) values(commenton, existingcomment,author);
      end if;

      return existingcomment;
      
   end;
$_$;


ALTER FUNCTION public.addcomment(integer, text, text) OWNER TO agrbrdf;

--
-- Name: addcomment(integer, text, text, boolean); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION addcomment(integer, text, text, boolean) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   declare 
      commenton alias for $1;
      commenttext alias for $2;
      author alias for $3;
      reuse alias for $4;
      mycur refcursor;
      existingcomment integer;
      commentonlsid varchar(2048);
      junk integer;
   begin

      /* get the lsid of the commented object */
      select xreflsid||':comment' into commentonlsid from ob where obid = commenton;

      if reuse then
         /* check if we can re-use a comment */
         existingcomment := null;
         open mycur for 
         select obid from commentob where commentstring = commenttext;
         fetch mycur into existingcomment;
         close mycur;
 
         if existingcomment is null then
            existingcomment := getNewObid();
            insert into commentob(obid, xreflsid, commentstring)
            values (existingcomment, commentonlsid, commenttext);
         end if;

         /* check if this object already commented with this comment */
         select ob into junk from commentlink where commentob = existingcomment and ob = commenton;
         if not FOUND then
            insert into commentlink(ob,commentob,commentby) values(commenton, existingcomment,author);
         end if;

         return existingcomment;
      else
         existingcomment := getNewObid();
         insert into commentob(obid, xreflsid, commentstring)
         values (existingcomment, commentonlsid, commenttext);
         insert into commentlink(ob,commentob,commentby) values(commenton, existingcomment,author);
      end if;

      return existingcomment;
      
   end;
$_$;


ALTER FUNCTION public.addcomment(integer, text, text, boolean) OWNER TO agrbrdf;

--
-- Name: addurl(integer, text, text, text, boolean); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION addurl(integer, text, text, text, boolean) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   declare 
      urlon alias for $1;
      urltext alias for $2;
      urladdress alias for $3;
      author alias for $4;
      reuse alias for $5;
      mycur refcursor;
      existingurl integer;
      junk integer;
   begin


      if reuse then
         /* check if we can re-use a link */
         existingurl := null;
         open mycur for 
         select obid from uriob where uristring = urladdress;
         fetch mycur into existingurl;
         close mycur;
 
         if existingurl is null then
            existingurl := getNewObid();
            insert into uriob(obid, xreflsid, uristring, uritype)
            values (existingurl, urladdress, urladdress,'URL');
         end if;

         /* check if this object already commented with this comment */
         select ob into junk from urilink where uriob = existingurl and ob = urlon;
         if not FOUND then
            insert into urilink(ob,uriob,displaystring,createdby) values(urlon, existingurl,urltext,author);
         end if;

         return existingurl;
      else
         existingurl := getNewObid();
         insert into uriob(obid, xreflsid, uristring, uritype)
         values (existingurl, urladdress, urladdress,'URL');
         insert into urilink(ob,uriob,displaystring,createdby) values(urlon, existingurl,urltext,author);
      end if;

      return existingurl;
      
   end;
$_$;


ALTER FUNCTION public.addurl(integer, text, text, text, boolean) OWNER TO agrbrdf;

--
-- Name: annotateorthologs(integer, integer, boolean, boolean); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION annotateorthologs(integer, integer, boolean, boolean) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
-- this uses the results of annotateReciprocalTophits, to annotate orthologs.
-- Orthologs can be annotated provided that the orthology relationship
-- between the databases is (at least) injective
-- The injective searh would be from a database consisting of, and only of, orthoseqs,
-- , to a database consisting of orthoseqs plus possibly additional seqs.
-- This algorithm enforces the injective ortholog relationship betwen the
-- databases.
--
   DECLARE
      querycursor refcursor;
      queryrecord record;
      lastquery integer;

      Injectionblastsearch ALIAS for $1;
      Surjectionblastsearch ALIAS for $2;
      annotateInjectionSearch ALIAS for $3;
      annotateSurjectionSearch ALIAS for $4;

      orthologcount integer;
   BEGIN   
      -- master query to loop through all seqs to be considered. The algorithm is simply to 
      -- annotate the first pair encountered for each query as ortholog pair.

      orthologcount := 0;
      lastquery := -1;

      open querycursor for
    select 
          i.querysequence,
           i.hitsequence,
           i.hitevalue + s.hitevalue as rpevalue,
           iaf.score + saf.score as rpscore
        from 
           ((databasesearchobservation i join
           databasesearchobservation s on
           i.querysequence = s.hitsequence and
           i.hitsequence = s.querysequence) join
           sequencealignmentfact iaf on iaf.databasesearchobservation = i.obid) join
           sequencealignmentfact saf on saf.databasesearchobservation = s.obid
        where
           i.databasesearchstudy = Injectionblastsearch and
           s.databasesearchstudy = Surjectionblastsearch and
           i.userflags like '%Best Reciprocal Hit%'
        order by
           i.querysequence,
           i.hitevalue + s.hitevalue asc,
           iaf.score + saf.score desc;
      fetch querycursor into queryrecord;

      while found  LOOP
         if lastquery != queryrecord.querysequence then
            if annotateInjectionSearch then
               update databasesearchobservation
               set userflags = coalesce(userflags || ',Ortholog', 'Ortholog'),
               lastupdateddate = now()
               where databasesearchstudy = Injectionblastsearch and 
               querysequence = queryrecord.querysequence and
               hitsequence = queryrecord.hitsequence;
            end if;

            if annotateSurjectionSearch then
               update databasesearchobservation
               set userflags = coalesce(userflags || ',Ortholog', 'Ortholog'),
               lastupdateddate = now()
               where databasesearchstudy = Surjectionblastsearch and
               hitsequence = queryrecord.querysequence  and
               querysequence = queryrecord.hitsequence;
            end if;

            orthologcount := orthologcount + 1;

         end if;

         lastquery := queryrecord.querysequence;

         fetch querycursor into queryrecord;
   
      end LOOP;

      close querycursor;

      return orthologcount;

    END;
$_$;


ALTER FUNCTION public.annotateorthologs(integer, integer, boolean, boolean) OWNER TO agrbrdf;

--
-- Name: annotateorthologs(integer, integer, boolean, boolean, boolean); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION annotateorthologs(integer, integer, boolean, boolean, boolean) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
-- this uses the results of annotateReciprocalTophits, to annotate orthologs.
-- Orthologs can be annotated provided that the orthology relationship
-- between the databases is (at least) injective
-- The injective searh would be from a database consisting of, and only of, orthoseqs,
-- , to a database consisting of orthoseqs plus possibly additional seqs.
-- This algorithm enforces the injective ortholog relationship betwen the
-- databases.
--
   DECLARE
      querycursor refcursor;
      queryrecord record;
      lastquery integer;

      Injectionblastsearch ALIAS for $1;
      Surjectionblastsearch ALIAS for $2;
      annotateInjectionSearch ALIAS for $3;
      annotateSurjectionSearch ALIAS for $4;
      usegenetable ALIAS for $5;

      orthologcount integer;
   BEGIN   
      -- master query to loop through all seqs to be considered. The algorithm is simply to 
      -- annotate the first pair encountered for each query as ortholog pair.

      orthologcount := 0;
      lastquery := -1;

      if not usegenetable then
        open querycursor for
    select 
          i.querysequence,
           i.hitsequence,
           i.hitevalue + s.hitevalue as rpevalue,
           iaf.score + saf.score as rpscore
        from 
           ((databasesearchobservation i join
           databasesearchobservation s on
           i.querysequence = s.hitsequence and
           i.hitsequence = s.querysequence) join
           sequencealignmentfact iaf on iaf.databasesearchobservation = i.obid) join
           sequencealignmentfact saf on saf.databasesearchobservation = s.obid
        where
           i.databasesearchstudy = Injectionblastsearch and
           s.databasesearchstudy = Surjectionblastsearch and
           i.userflags like '%Best Reciprocal Hit%'
        order by
           i.querysequence,
           i.hitevalue + s.hitevalue asc,
           iaf.score + saf.score desc;
      else
        open querycursor for
    select 
           gpl.geneticob as gene,
          i.querysequence,
           i.hitsequence,
           i.hitevalue + s.hitevalue as rpevalue,
           iaf.score + saf.score as rpscore
        from 
           (((databasesearchobservation i join
           databasesearchobservation s on
           i.querysequence = s.hitsequence and
           i.hitsequence = s.querysequence) join
           sequencealignmentfact iaf on iaf.databasesearchobservation = i.obid) join
           sequencealignmentfact saf on saf.databasesearchobservation = s.obid) join
           geneproductlink gpl on gpl.biosequenceob = i.querysequence
        where
           i.databasesearchstudy = Injectionblastsearch and
           s.databasesearchstudy = Surjectionblastsearch and
           i.userflags like '%Best Reciprocal Hit%' 
        order by
           gpl.geneticob,
           i.hitevalue + s.hitevalue asc,
           iaf.score + saf.score desc;
      end if;

      fetch querycursor into queryrecord;

      while found  LOOP
         if not usegenetable then
            if lastquery != queryrecord.querysequence then
               if annotateInjectionSearch then
                  update databasesearchobservation
                  set userflags = coalesce(userflags || ',Ortholog', 'Ortholog'),
                  lastupdateddate = now()
                  where databasesearchstudy = Injectionblastsearch and 
                  querysequence = queryrecord.querysequence and
                  hitsequence = queryrecord.hitsequence;
               end if;

               if annotateSurjectionSearch then
                  update databasesearchobservation
                  set userflags = coalesce(userflags || ',Ortholog', 'Ortholog'),
                  lastupdateddate = now()
                  where databasesearchstudy = Surjectionblastsearch and
                  hitsequence = queryrecord.querysequence  and
                  querysequence = queryrecord.hitsequence;
               end if;
               orthologcount := orthologcount + 1;
            end if;
            lastquery := queryrecord.querysequence;
         else
            if lastquery != queryrecord.gene then
               if annotateInjectionSearch then
                  update databasesearchobservation
                  set userflags = coalesce(userflags || ',Ortholog', 'Ortholog'),
                  lastupdateddate = now()
                  where databasesearchstudy = Injectionblastsearch and 
                  querysequence = queryrecord.querysequence and
                  hitsequence = queryrecord.hitsequence;
               end if;

               if annotateSurjectionSearch then
                  update databasesearchobservation
                  set userflags = coalesce(userflags || ',Ortholog', 'Ortholog'),
                  lastupdateddate = now()
                  where databasesearchstudy = Surjectionblastsearch and
                  hitsequence = queryrecord.querysequence  and
                  querysequence = queryrecord.hitsequence;
               end if;
               orthologcount := orthologcount + 1;
            end if;   
            lastquery := queryrecord.gene;
      
         end if;

         fetch querycursor into queryrecord;
   
      end LOOP;

      close querycursor;

      return orthologcount;

    END;
$_$;


ALTER FUNCTION public.annotateorthologs(integer, integer, boolean, boolean, boolean) OWNER TO agrbrdf;

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

--
-- Name: annotatesnp(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION annotatesnp(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   SNPid alias for $1;
   annotationtype alias for $2;
   animalClass alias for $3;
 
   cursClasses refcursor;
   ClassToSummarise character varying (2048);

   cursGenotype refcursor;
   GenotypeToProcess character varying (2);

   alleleCountA int4;
   alleleCountC int4;
   alleleCountG int4;
   alleleCountT int4;
   alleleCountUnknown int4;
   alleleCountTotal int4;

  testoutput character varying (200);
begin
  --open query to get all classes we want to summarise   

  OPEN cursClasses FOR 
	SELECT xreflsid
	from 
	  oblist
	where
	  xreflsid like animalClass;
  LOOP
    FETCH cursClasses into ClassToSummarise;

    IF NOT FOUND THEN
      EXIT;
    END IF;

 -- for each class
   -- open query to return all genotypes for this SNP for all animals in class, 
   -- for the SNPid passed in as an arg to the function

    alleleCountA = 0;
    alleleCountC = 0;
    alleleCountG = 0;
    alleleCountT = 0;
    alleleCountUnknown = 0;
    alleleCountTotal = 0;

    OPEN cursGenotype FOR
	SELECT
          getCanonicalGenotype(gto.genotypeobserved) as genotype
        from
          (((oblist o join listmembershiplink l on 
             o.xreflsid = ClassToSummarise  and
             l.oblist = o.obid) join
             biosamplingfunction b on b.biosubjectob = l.ob) join
             genotypestudy g on g.biosampleob = b.biosampleob) join
             genotypeobservation gto on gto.genotypestudy = g.obid and
             gto.genetictestfact = SNPid;

    LOOP
      FETCH cursGenotype into GenotypeToProcess;

      IF NOT FOUND THEN
        EXIT;
      END IF;

      -- for each record
      -- accumulate stats
    
      alleleCountTotal = alleleCountTotal + 2; 

      IF SUBSTR(GenotypeToProcess,1,1) = 'A' THEN
	alleleCountA = alleleCountA + 1;
      END IF;

      IF SUBSTR(GenotypeToProcess,2,1) = 'A' THEN
	alleleCountA = alleleCountA + 1;
      END IF;
      
      IF SUBSTR(GenotypeToProcess,1,1) = 'C' THEN
	alleleCountC = alleleCountC + 1;
      END IF;
      IF SUBSTR(GenotypeToProcess,2,1) = 'C' THEN
	alleleCountC = alleleCountC + 1;
      END IF;
      
      IF SUBSTR(GenotypeToProcess,2,1) = 'G' THEN
	alleleCountG = alleleCountG + 1;
      END IF;
      IF SUBSTR(GenotypeToProcess,1,1) = 'G' THEN
	alleleCountG = alleleCountG + 1;
      END IF;
      
      IF SUBSTR(GenotypeToProcess,1,1) = 'T' THEN
	alleleCountT = alleleCountT + 1;
      END IF;
      IF SUBSTR(GenotypeToProcess,2,1) = 'T' THEN
	alleleCountT = alleleCountT + 1;
      END IF;
            
      IF GenotypeToProcess = '??' THEN
	alleleCountUnknown = alleleCountUnknown + 2;
      END IF;
  
    END LOOP;

    CLOSE cursGenotype;
    -- write accumulated stats to table

    IF alleleCountTotal > 0 THEN
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_A', alleleCountA);
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_C', alleleCountC);
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_G', alleleCountG);
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_T', alleleCountT);
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_Unknown', alleleCountUnknown);
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_All', alleleCountTotal);

    END IF;

  END LOOP;
  CLOSE cursClasses;
  RETURN   'TRUE'; -- to_char(alleleCountT, '99999D99');  -- testoutput; 
end;
$_$;


ALTER FUNCTION public.annotatesnp(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: FUNCTION annotatesnp(integer, character varying, character varying); Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON FUNCTION annotatesnp(integer, character varying, character varying) IS 'This function adds annotation (allele frequency etc) to the genetictestfact2 table';


--
-- Name: blastn_results_tophit_field(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION blastn_results_tophit_field(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      sqlstmnt varchar;
      queryid alias for $1;
      attributename alias for $2;
      rec record;
   BEGIN
      sqlstmnt := 'select '
        || attributename || ' as selectedfield ' 
        || ' from blastn_results where queryid = '''  
        || queryid 
        || ''' order by evalue limit 1';
      for rec in execute sqlstmnt loop
         return rec.selectedfield;
         exit;
      end loop;
   END;
$_$;


ALTER FUNCTION public.blastn_results_tophit_field(character varying, character varying) OWNER TO agrbrdf;

--
-- Name: blastn_results_tophit_floatfield(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION blastn_results_tophit_floatfield(character varying, character varying) RETURNS double precision
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      sqlstmnt varchar;
      queryid alias for $1;
      attributename alias for $2;
      rec record;
   BEGIN
      sqlstmnt := 'select '
        || attributename || ' as selectedfield ' 
        || ' from blastn_results where queryid = '''  
        || queryid 
        || ''' order by evalue limit 1';
      for rec in execute sqlstmnt loop
         return rec.selectedfield;
         exit;
      end loop;
   END;
$_$;


ALTER FUNCTION public.blastn_results_tophit_floatfield(character varying, character varying) OWNER TO agrbrdf;

--
-- Name: blastx_results_tophit_field(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION blastx_results_tophit_field(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      sqlstmnt varchar;
      queryid alias for $1;
      attributename alias for $2;
      rec record;
   BEGIN
      sqlstmnt := 'select '
        || attributename || ' as selectedfield ' 
        || ' from blastx_results where queryid = '''  
        || queryid 
        || ''' order by evalue limit 1';
      for rec in execute sqlstmnt loop
         return rec.selectedfield;
         exit;
      end loop;
   END;
$_$;


ALTER FUNCTION public.blastx_results_tophit_field(character varying, character varying) OWNER TO agrbrdf;

--
-- Name: blastx_results_tophit_textfield(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION blastx_results_tophit_textfield(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      sqlstmnt varchar;
      queryid alias for $1;
      attributename alias for $2;
      rec record;
   BEGIN
      sqlstmnt := 'select substr('
        || attributename || ',1,80) as selectedfield '
        || ' from blastx_results where queryid = '''
        || queryid
        || ''' order by evalue limit 1';
      for rec in execute sqlstmnt loop
         return rec.selectedfield;
         exit;
      end loop;
   END;
$_$;


ALTER FUNCTION public.blastx_results_tophit_textfield(character varying, character varying) OWNER TO agrbrdf;

--
-- Name: checkaccesslinkkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkaccesslinkkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'key error - obid not found';
        end if;

        --the list should have type USR ROLE
        if oblist is not null then
        end if;



        return NEW;
    END;
$$;


ALTER FUNCTION public.checkaccesslinkkey() OWNER TO agrbrdf;

--
-- Name: checkaccessontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkaccessontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologyTermFact where termname = NEW.accessType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'ACCESS_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid access type ', NEW.accessType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkaccessontology() OWNER TO agrbrdf;

--
-- Name: checkaliquotrecord(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkaliquotrecord() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        units RECORD;
        terms RECORD;
    BEGIN
        if NEW.aliquotweightunit is not null then
           select into units  * from ontologytermfact where termname = NEW.aliquotweightunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.aliquotweightunit;
           end if;
        end if;

        if NEW.aliquotvolumeunit is not null then
           select into units  * from ontologytermfact where termname = NEW.aliquotvolumeunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.aliquotvolumeunit;
           end if;
        end if;

        if NEW.aliquotdmeunit is not null then
           select into units  * from ontologytermfact where termname = NEW.aliquotdmeunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.aliquotdmeunit;
           end if;
        end if;

        return NEW;
    END;
$$;


ALTER FUNCTION public.checkaliquotrecord() OWNER TO agrbrdf;

--
-- Name: checkanalysisfunctionobkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkanalysisfunctionobkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'checkanalysisfunctionobkey : key error - obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkanalysisfunctionobkey() OWNER TO agrbrdf;

--
-- Name: checkanalysistypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkanalysistypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.procedureType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'ANALYSIS_PROCEDURE_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid analysis procedure type ', NEW.procedureType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkanalysistypeontology() OWNER TO agrbrdf;

--
-- Name: checkbiodatabasetype(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkbiodatabasetype() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.databaseType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'BIODATABASETYPE_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid biodatabase type ', NEW.databaseType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkbiodatabasetype() OWNER TO agrbrdf;

--
-- Name: checkbiolibrarytypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkbiolibrarytypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.libraryType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'BIOLIBRARY_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid library type ', NEW.libraryType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkbiolibrarytypeontology() OWNER TO agrbrdf;

--
-- Name: checkbioprotocoltypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkbioprotocoltypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.protocolType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'BIOPROTOCOL_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid protocol type ', NEW.protocolType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkbioprotocoltypeontology() OWNER TO agrbrdf;

--
-- Name: checkbiosampletypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkbiosampletypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.sampleType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'BIOSAMPLE_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid sample type ', NEW.sampleType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkbiosampletypeontology() OWNER TO agrbrdf;

--
-- Name: checkcommentedobkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkcommentedobkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        if NEW.commentedOb is not null then
           select obid into NEW.commentedOb from ob where obid = NEW.commentedOb;
           if not FOUND then
              RAISE EXCEPTION 'key error - commentedOb not found';
           end if;
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkcommentedobkey() OWNER TO agrbrdf;

--
-- Name: checkcommentlinkkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkcommentlinkkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'key error - obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkcommentlinkkey() OWNER TO agrbrdf;

--
-- Name: checkdatabasesearchstudytypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkdatabasesearchstudytypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.studyType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'DATABASESEARCHSTUDYTYPE_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid studytype ', NEW.studyType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkdatabasesearchstudytypeontology() OWNER TO agrbrdf;

--
-- Name: checkdatasourceontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkdatasourceontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.dataSourceType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'DATASOURCE_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid datasource type ', NEW.dataSourceType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkdatasourceontology() OWNER TO agrbrdf;

--
-- Name: checkdisplayfunctionobkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkdisplayfunctionobkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'checkdisplayfunctionobkey : key error - obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkdisplayfunctionobkey() OWNER TO agrbrdf;

--
-- Name: checkfeatureattributeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkfeatureattributeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.attributeName and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'SEQUENCE_FEATURE_ATTRIBUTE_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid feature attribute name ', NEW.attributeName;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkfeatureattributeontology() OWNER TO agrbrdf;

--
-- Name: checkfeatureontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkfeatureontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.featureType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'SEQUENCE_FEATURE_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid feature name ', NEW.featureType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkfeatureontology() OWNER TO agrbrdf;

--
-- Name: checkgeneexpressionstudytypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkgeneexpressionstudytypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.studyType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'GENEEXPRESSIONSTUDYTYPE_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid studytype term ', NEW.studyType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkgeneexpressionstudytypeontology() OWNER TO agrbrdf;

--
-- Name: checkgeneticlistontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkgeneticlistontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.listType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'GENETIC_LIST_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid genetic list type ', NEW.listType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkgeneticlistontology() OWNER TO agrbrdf;

--
-- Name: checkgeneticobontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkgeneticobontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.geneticObType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'GENETICOB_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid genetic ob type ', NEW.geneticObType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkgeneticobontology() OWNER TO agrbrdf;

--
-- Name: checkgenetictestontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkgenetictestontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.testType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'GENETICTEST_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid testtype  ', NEW.testType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkgenetictestontology() OWNER TO agrbrdf;

--
-- Name: checkgenotypestudytypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkgenotypestudytypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.studyType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'GENOTYPESTUDY_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid studytype term ', NEW.studyType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkgenotypestudytypeontology() OWNER TO agrbrdf;

--
-- Name: checkimportobkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkimportobkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'checkimportobkey : key error - obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkimportobkey() OWNER TO agrbrdf;

--
-- Name: checklabresourceontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checklabresourceontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.resourceType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'LABRESOURCE_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid lab resource type ', NEW.resourceType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checklabresourceontology() OWNER TO agrbrdf;

--
-- Name: checklistontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checklistontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.listType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'LIST_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid list type ', NEW.listType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checklistontology() OWNER TO agrbrdf;

--
-- Name: checkliteraturereferencelinkkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkliteraturereferencelinkkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'key error - obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkliteraturereferencelinkkey() OWNER TO agrbrdf;

--
-- Name: checkoblistkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkoblistkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'key error - obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkoblistkey() OWNER TO agrbrdf;

--
-- Name: checkpedigreeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkpedigreeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.relationship and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'PEDIGREE_RELATIONSHIP');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid pedigree relationship ', NEW.relationship;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkpedigreeontology() OWNER TO agrbrdf;

--
-- Name: checkphenotypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkphenotypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.phenotypeTerm and 
                       ontologyob = (select obid from ontologyOb where ontologyName = (
                          select phenotypeOntologyName from phenotypeStudy where obid = NEW.phenotypestudy));
        if not FOUND then
           RAISE EXCEPTION '% is not a valid phenotype term ', NEW.phenotypeTerm;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkphenotypeontology() OWNER TO agrbrdf;

--
-- Name: checkphenotypeontologyname(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkphenotypeontologyname() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        names RECORD;
    BEGIN
        select into names  * from ontologyOb where ontologyName = NEW.phenotypeOntologyName;
        if not FOUND then
           RAISE EXCEPTION '% is not a valid phenotype ontology ', NEW.phenotypeOntologyName;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkphenotypeontologyname() OWNER TO agrbrdf;

--
-- Name: checkpredicatekeys(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkpredicatekeys() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select a.obid , b.obid into NEW.subjectob,NEW.objectob from ob a, ob b  where a.obid = NEW.subjectob and b.obid = NEW.objectob;
        if not FOUND then
           RAISE EXCEPTION 'key error - subject or object obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkpredicatekeys() OWNER TO agrbrdf;

--
-- Name: checkpredicateontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkpredicateontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.predicate and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'PREDICATE_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid predicate type ', NEW.predicate;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkpredicateontology() OWNER TO agrbrdf;

--
-- Name: checksampleunits(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checksampleunits() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        units RECORD;
    BEGIN
        if NEW.sampleweightunit is not null then
           select into units  * from ontologytermfact where termname = NEW.sampleweightunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.sampleweightunit;
           end if;
        end if;

        if NEW.samplevolumeunit is not null then
           select into units  * from ontologytermfact where termname = NEW.samplevolumeunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.samplevolumeunit;
           end if;
        end if;

        if NEW.sampledmeunit is not null then
           select into units  * from ontologytermfact where termname = NEW.sampledmeunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.sampledmeunit;
           end if;
        end if;

        return NEW;
    END;
$$;


ALTER FUNCTION public.checksampleunits() OWNER TO agrbrdf;

--
-- Name: checksecurityfunctionobkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checksecurityfunctionobkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        if NEW.ob is not null then
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'checksecurityfunctionobkey : key error - obid not found';
        end if;
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checksecurityfunctionobkey() OWNER TO agrbrdf;

--
-- Name: checksequenceontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checksequenceontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.sequenceType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'AGSEQUENCE_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid sequence type ', NEW.sequenceType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checksequenceontology() OWNER TO agrbrdf;

--
-- Name: checkunitname(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkunitname() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        units RECORD;
    BEGIN
        if NEW.unitName is not null then
           select into units  * from ontologytermfact where termname = NEW.unitName and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.unitName;
           else
              return NEW;
           end if;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkunitname() OWNER TO agrbrdf;

--
-- Name: checkurilinkkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkurilinkkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'key error - obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkurilinkkey() OWNER TO agrbrdf;

--
-- Name: checkvoptypeid(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkvoptypeid() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        if NEW.voptypeid is not null then
           select obtypeid into NEW.voptypeid from obtype where obtypeid = NEW.voptypeid and isop ;
           if not FOUND then
              RAISE EXCEPTION 'key error - voptypeid to insert is not a valid op type ';
           end if;
        end if;

        return NEW;
    END;
$$;


ALTER FUNCTION public.checkvoptypeid() OWNER TO agrbrdf;

--
-- Name: checkworkflowontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkworkflowontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.workFlowStageType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'WORKFLOW_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid workflow stage type ', NEW.workFlowStageType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkworkflowontology() OWNER TO agrbrdf;

--
-- Name: comma_concat(text, text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION comma_concat(text, text) RETURNS text
    LANGUAGE plpgsql
    AS $_$
   declare
      arg1 alias for $1;
      arg2 alias for $2;
   begin
      if length(arg1) > 0 then
         return arg1||','||arg2 ;
      else
         return arg1||arg2 ;
      end if;
   end;
$_$;


ALTER FUNCTION public.comma_concat(text, text) OWNER TO agrbrdf;

--
-- Name: comment_concat(text, text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION comment_concat(text, text) RETURNS text
    LANGUAGE plpgsql
    AS $_$
   declare
      arg1 alias for $1;
      arg2 alias for $2;
   begin
      return arg1||'
====================Begin Comment====================
'||arg2 || '
====================End Comment====================
';
   end;
$_$;


ALTER FUNCTION public.comment_concat(text, text) OWNER TO agrbrdf;

--
-- Name: concatdatasourcefacts(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION concatdatasourcefacts(integer, character varying, character varying) RETURNS text
    LANGUAGE plpgsql
    AS $_$
   declare 
      mylist alias for $1;
      mynamespace alias for $2;
      myattributename alias for $3;
      result text;
   begin
      select agg_newline_concat(df.attributevalue) into result 
      from 
      datasourcelistmembershiplink dl join datasourcefact df on
      df.datasourceob = dl.datasourceob
      where
      dl.datasourcelist = mylist;
      return result;
   end;
$_$;


ALTER FUNCTION public.concatdatasourcefacts(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: depipe(character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION depipe(character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   instring alias for $1;
begin
   return lasttoken(instring,'|');
end;$_$;


ALTER FUNCTION public.depipe(character varying) OWNER TO agrbrdf;

--
-- Name: filterkeywords(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION filterkeywords() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select lower(NEW.obkeywords) into NEW.obkeywords;
        return NEW;
    END;
$$;


ALTER FUNCTION public.filterkeywords() OWNER TO agrbrdf;

--
-- Name: format_evalue(double precision); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION format_evalue(double precision) RETURNS character varying
    LANGUAGE plpgsql IMMUTABLE STRICT
    AS $_$
declare
   evalue alias for $1;
   mantissa double precision;
   exponent integer;
   strevalue varchar;
begin
   strevalue := '';
   if evalue = 0.0 then
      strevalue := '0.0';
   else 
      exponent := round(log(evalue));
      mantissa := evalue/power(10,exponent);
      strevalue := to_char(mantissa,'999.999') || 'e' || rtrim(ltrim(to_char(exponent,'99999')));
   end if;

   return strevalue;
end
$_$;


ALTER FUNCTION public.format_evalue(double precision) OWNER TO agrbrdf;

--
-- Name: from_hex(text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION from_hex(t text) RETURNS integer
    LANGUAGE plpgsql IMMUTABLE STRICT
    AS $$
  DECLARE
    r RECORD;
  BEGIN
    FOR r IN EXECUTE 'SELECT x'''||t||'''::integer AS hex' LOOP
      RETURN r.hex;
    END LOOP;
  END
$$;


ALTER FUNCTION public.from_hex(t text) OWNER TO agrbrdf;

--
-- Name: getaccessionfromgeneid(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getaccessionfromgeneid(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   arggeneid alias for $1;
   reftype alias for $2;
   refseqcur refcursor;
   refresult varchar;
begin
   refresult := null;
   if arggeneid is null then
      return null;
   else
      if reftype = 'mRNA' then
         open refseqcur for 
         select rna_nucleotide_accession from gene2accession where
         geneid = arggeneid and rna_nucleotide_accession  != '-';
      elsif reftype = 'protein' then
         open refseqcur for 
         select protein_accession from gene2accession where
         geneid = arggeneid and protein_accession != '-';
      end if;

      fetch refseqcur into refresult;
      close refseqcur;

   end if;

   return refresult;

end;$_$;


ALTER FUNCTION public.getaccessionfromgeneid(character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getaffyprobenormalisationfactor(integer, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getaffyprobenormalisationfactor(integer, integer) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        geneexpressionstudy ALIAS for $1;
        microarrayspotfact ALIAS for $2;
        species varchar;
        factor varchar;
    BEGIN

        -- first get the species classification
        open factcursor for
        select 
           getBioSequenceFact(p.objectob,'Affy Annotation','Species classification (E=endophyte, R=ryegrass, G=Glomeromycetes, B=bacterial control, U=unknown, Junk=not detectable)' )
        from
           predicatelink p where 
           p.predicate = 'ARRAYSPOT-SEQUENCE' and
           p.subjectob = microarrayspotfact; -- example : 4460195
        fetch factcursor into species;

        if not FOUND then 
           close factcursor;
           return null;
        end if;


        if species = null then
           return null;
        elsif species = 'R' then
           factor := getgeneexpressionstudycharfact(geneexpressionstudy,'Normalisation','Ryegrass Factor'); -- example : 4978342
        elsif species = 'E' then
           factor := getgeneexpressionstudycharfact(geneexpressionstudy,'Normalisation','Endophyte Factor');
        else
           return null;
        end if;


        return factor;
    END;
$_$;


ALTER FUNCTION public.getaffyprobenormalisationfactor(integer, integer) OWNER TO agrbrdf;

--
-- Name: getagresearchfastarecord(character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getagresearchfastarecord(character varying) RETURNS text
    LANGUAGE plpgsql
    AS $_$  

DECLARE
   cursr refcursor;

   biosequenceobid integer;
   seqname varchar;
   seqbuff text;
   strbuff text;

BEGIN
   --Test if obid is an obid or is an xreflsid
   select into biosequenceobid obid from biosequenceob where xreflsid = $1;
   if not FOUND then
      biosequenceobid := $1;
   end if;
   
   strbuff := '';

   open cursr for
    select
       xreflsid ,
       seqstring
    from
       biosequenceob
    where
       obid = biosequenceobid;
    
   fetch cursr into seqname, seqbuff;

   close cursr;
   
   strbuff := '>'||seqname||chr(10)||seqbuff;
   

   return strbuff;
END
$_$;


ALTER FUNCTION public.getagresearchfastarecord(character varying) OWNER TO agrbrdf;

--
-- Name: getallelefrequency(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getallelefrequency(integer, character varying, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
declare
   SNPid alias for $1;
   animalClass alias for $2;
   allelearg alias for $3;
   cursGenotype refcursor;
   GenotypeToProcess character varying (2);

   alleleCount integer;

begin
  --open query to get all classes we want to summarise   

    OPEN cursGenotype FOR
	SELECT
          getCanonicalGenotype(gto.genotypeobserved) as genotype
        from
          (((oblist o join listmembershiplink l on 
             o.xreflsid = animalClass  and
             l.oblist = o.obid) join
             biosamplingfunction b on b.biosubjectob = l.ob) join
             genotypestudy g on g.biosampleob = b.biosampleob) join
             genotypeobservation gto on gto.genotypestudy = g.obid and
             gto.genetictestfact = SNPid;

    alleleCount := 0;
    LOOP
      FETCH cursGenotype into GenotypeToProcess;

      IF NOT FOUND THEN
        EXIT;
      END IF;


      IF GenotypeToProcess = '??' and (upper(allelearg) = 'UNKNOWN' or allelearg = '??') THEN
        alleleCount := alleleCount + 2;
      ELSE
        IF upper(SUBSTR(GenotypeToProcess,1,1)) = upper(allelearg) THEN
	  alleleCount := alleleCount + 1;
        END IF;

        IF upper(SUBSTR(GenotypeToProcess,2,1)) = upper(allelearg) THEN
	  alleleCount := alleleCount + 1;
        END IF;
      END IF;
    END LOOP;

    CLOSE cursGenotype;
    -- write accumulated stats to table

  RETURN   alleleCount; 
end;
$_$;


ALTER FUNCTION public.getallelefrequency(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getattributefromaccession(character varying, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getattributefromaccession(character varying, integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
declare
   locatorcur refcursor;
   argaccession0 alias for $1;
   maxversion alias for $2;
   attributename alias for $3;
   geneidres integer;
   tax_idres integer;
   argaccession varchar(64);
   tryaccession varchar(64);
   tryversion integer;
begin
   geneidres := null;

   if argaccession0 is null then
      return null;
   end if;

   argaccession := ltrim(rtrim(argaccession0));

--return errorMessage;

   -- first check format of input - check not too many dots
   if length(argaccession) - length(replace(argaccession,'.','')) > 1 then
      raise exception 'Bad accession format in argument ';
   end if;

   for tryversion in 0..maxVersion loop
      if tryversion > 0 then
         -- dePipe handles cases like ref|NM_blah| that often end up in our database
         tryaccession := dePipe(upper(split_part(argaccession,'.',1) || '.' || ltrim(rtrim(to_char(tryVersion,'9999')))));
         --raise notice '%' , tryaccession;
      else
         tryaccession := dePipe(upper(argaccession));
      end if;

      -- try each accession type - i.e. RNA,protein,Genomic.
      begin
         open locatorcur for
         select
            geneid,
            tax_id
         from
            gene2accession
         where
            rna_nucleotide_accession = tryaccession;
         fetch locatorcur into geneidres, tax_idres;
      exception
         when others then -- should be when no_data but this exception not known for some reason
         null;
      end;
      close locatorcur ;
      exit when geneidres is not null;


      begin
         open locatorcur for
         select
            geneid, 
            tax_id
         from
            gene2accession
         where
            protein_accession = tryaccession;
         fetch locatorcur into geneidres, tax_idres;
      exception
         when others then
         null;
      end;
      close locatorcur ;
      exit when geneidres is not null;

   end loop; -- try the argaccession, and if no hit, then try all versions of it


   if attributename = 'geneid' then
      return geneidres;
   else
      return tax_idres;
   end if;

end;$_$;


ALTER FUNCTION public.getattributefromaccession(character varying, integer, character varying) OWNER TO agrbrdf;

--
-- Name: getbiodatabasecharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getbiodatabasecharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        databaseobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from biodatabasefact 
      where biodatabaseob = databaseobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getbiodatabasecharfact(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getbiosequencefact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getbiosequencefact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        sequenceobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from bioSequenceFact 
      where bioSequenceOb = sequenceobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getbiosequencefact(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getcanonicalgenotype(character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getcanonicalgenotype(character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   rawarggenotype alias for $1;
   arggenotype varchar(32);
   allele1 varchar(32);
   allele2 varchar(32);
   canonicalgenotype varchar(32);
begin
   arggenotype = trim(rawarggenotype);  
   canonicalgenotype := '??';

   if (arggenotype not like '%?%') and (upper(arggenotype) not like '%UNKNOWN%')  then
      allele1 = substr(arggenotype, 1, 1);
      allele2 = substr(arggenotype, 2, 1);
      if allele1 is not null and allele2 is not null then
         if length(allele1) > 0 and length(allele2) > 0 then
            if allele1 <= allele2 then
               canonicalgenotype := upper(allele1 || allele2);
            else
               canonicalgenotype := upper(allele2 || allele1);
            end if;
         end if;
      end if;
   end if;
   return canonicalgenotype;
end;
$_$;


ALTER FUNCTION public.getcanonicalgenotype(character varying) OWNER TO agrbrdf;

--
-- Name: FUNCTION getcanonicalgenotype(character varying); Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON FUNCTION getcanonicalgenotype(character varying) IS 'This function tidies up the raw genotype and returns in a canonical format. E.G. GC becomes CG ; ?T becomes ?? etc';


--
-- Name: getdatasourcecharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getdatasourcecharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        datasourceobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from datasourcefact 
      where datasourceob = datasourceobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getdatasourcecharfact(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getdescriptivelistmembership(integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getdescriptivelistmembership(integer) RETURNS text
    LANGUAGE plpgsql
    AS $_$
   declare 
      myob alias for $1;
      result text;
   begin
      select 
         --agg_comma_concat(split_part(l.listdefinition,':',1)) into result 
         agg_comma_concat(l.listdefinition) into result 
      from
         listmembershiplink lml join oblist l on
         l.obid = lml.oblist
      where
         lml.ob = myob;
      return result;
   end;
$_$;


ALTER FUNCTION public.getdescriptivelistmembership(integer) OWNER TO agrbrdf;

--
-- Name: getgenbankrecord(character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getgenbankrecord(character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
DECLARE
   cursr refcursor;
   speciesVal varchar;
   taxidVal varchar;
   source varchar;
   
   seqname varchar;
   seqtypeholder varchar;
   seqlen integer;
   seqstr varchar;
   seqtype varchar;
   seqtop varchar;
   seqdate date;

   feattype varchar;
   featstart integer;
   featstop integer;
   featxref varchar;
   featcom varchar;
   featevid varchar;

   --biosequenceobid ALIAS for $1;
   biosequenceobid integer;
   seqbuff varchar;
   strbuff varchar;

   comments varchar;
   position integer;
   basesize integer;
   lastfeature varchar;
   lastseqstart integer;
   lastseqstop integer;

BEGIN
   --Test if obid is an obid or is an xreflsid
   select into biosequenceobid obid from biosequenceob where xreflsid = $1;
   if not FOUND then
      select into biosequenceobid obid from biosequenceob where obid = $1;
   end if;
   if not FOUND then
      return 'ERROR - obid not found!';
   end if;
   
   strbuff := '';

   open cursr for
    select
       sequencename,    --name                                 seqname
       seqlength,       --number of bps or aas               seqlen
       seqstring,       --dna/aa sequence                      seqstr
       sequencetype,    --type of sequence, eg "genomic DNA"   seqtype
       sequencetopology,--type of sequence, eg "genomic DNA"   seqtop
       createddate      --date record was created              seqdate
    from
       biosequenceob
    where
       obid = biosequenceobid;
    
   fetch cursr into seqname, seqlen, seqstr, seqtype, seqtop, seqdate;

   close cursr;
   
   if (strpos(seqtype,'RNA') > 0) then
      seqtypeholder = ' bp    RNA';
   elsif (strpos(seqtype,'DNA') > 0) then
      seqtypeholder = ' bp    DNA';
   elsif (strpos(seqtype,'PROTEIN') > 0) then
      seqtypeholder = ' aa       ';
   else
      seqtypeholder = '          ';
   end if;

   -- LOCUS       <externalname>
   if (length(seqname)<25) then
      seqbuff := 'LOCUS       '||rpad(seqname, 25, ' ');
   else 
      seqbuff := 'LOCUS       '||seqname||' ';
   end if;
   strbuff := strbuff||seqbuff;
   
   seqbuff := seqlen||
        seqtypeholder||'     '||
        seqtop||'   '||
        '    '|| --MAM, INV, etc (the genus? e.g. Mammal, Invertebrate - is this recorded?)
        to_char(seqdate, 'DD-MON-YYYY')||chr(10);
   strbuff := strbuff||seqbuff;

   -- ACCESSION   <externalname>
   seqbuff := 'ACCESSION   '||seqname||chr(10);
   strbuff := strbuff||seqbuff;

    -- SOURCE      AgResearch
   select into source su.subjectspeciesname 
   from biosubjectob su, biosamplingfunction f, biosampleob sa, sequencingfunction se
   where su.obid = f.biosubjectob
   and f.biosampleob = sa.obid
   and sa.obid = se.biosampleob
   and se.biosequenceob = biosequenceobid;
   
   if FOUND then 
      seqbuff := 'SOURCE      '||source||chr(10);
      strbuff := strbuff||seqbuff;
   end if;
    
   open cursr for
    select
       speciesname, --speciesVal
       speciestaxid --taxidVal
    from
       geneticlocationfact 
    where
       biosequenceob = biosequenceobid
       and speciestaxid is not null;

   fetch cursr into speciesVal, taxidVal;

   close cursr;
   
   if NOT FOUND then --is this right? Will it do what I want???
      speciesVal := '';
      taxidVal := '';
   end if;

   -- TAXON (Source Organism)
   if speciesVal != '' then
      seqbuff := '  ORGANISM  '||speciesVal||chr(10);
      strbuff := strbuff||seqbuff;
   end if;

   open cursr for
     select
        featuretype,    --feature title  feattype
        featurestart,   --start pos      featstart
        featurestop,    --stop pos       featstop
        xreflsid,       --/db_xref=      featxref
        featurecomment, --/note=         featcom
        evidence        --/evidence=     featevid
     from
        biosequencefeaturefact
     where
        biosequenceob = biosequenceobid
     order by
        featurestart,
        featurestop,
        featuretype;
   
   fetch cursr into feattype, featstart, featstop, featxref, featcom, featevid;
   
   -- FEATURES
   if (speciesVal != '') or FOUND then
      seqbuff := 'FEATURES              Location/Qualifiers'||chr(10);
      strbuff := strbuff||seqbuff;
   end if;

   -- TAXON (Feature)
   if (speciesVal != '') then
      seqbuff := '     source           1..'||seqlen||chr(10);
      strbuff := strbuff||seqbuff;
      seqbuff := '                     /organism="'||speciesVal||'"'||chr(10);
      strbuff := strbuff||seqbuff;
      if (taxidVal != '') then
          seqbuff := '                     /db_xref="taxon:'||taxidVal||'"'||chr(10);
          strbuff := strbuff||seqbuff;
      end if;
   end if;

   -- CDS and GENES
   lastfeature := 'blurb';
   lastseqstart := -1;
   lastseqstop := -1;
   while FOUND loop
      if (feattype <> lastfeature or featstart <> lastseqstart or featstop <> lastseqstop) then
         if featstop >= featstart then
            seqbuff := '     '||rpad(feattype,16,' ')||featstart||'..'||featstop||chr(10);
         else
            seqbuff := '     '||rpad(feattype,16,' ')||'complement('||featstop||'..'||featstart||')'||chr(10);
         end if;
         strbuff := strbuff||seqbuff;
         lastfeature := feattype;
         lastseqstart := featstart;
         lastseqstop := featstop;
      end if;
      if (featxref != '') then
         seqbuff := '                     /db_xref="'||featxref||'"'||chr(10);
         strbuff := strbuff||seqbuff;
      end if;
      if (featevid != '') then
         seqbuff := '                     /evidence="'||featevid||'"'||chr(10);
         strbuff := strbuff||seqbuff;
      end if;
      if (featcom != '') then
         seqbuff := '                     /comment="'||featcom||'"'||chr(10);
         strbuff := strbuff||seqbuff;
      end if;
      fetch cursr into feattype, featstart, featstop, featxref, featcom, featevid;
   end loop;

   close cursr;
   
/*   -- COMMENTS formatted into lines of 68 chars plus 'COMMENT     '
   comments := getAgResearchGenbankComments(seqname,dbname);
   if (length(comments) > 0) then
      seqbuff := rpad('COMMENT',12,' ');
      strbuff := strbuff||seqbuff;
      position := 1;
      basesize := 68;
      while (position <= length(comments)) loop
         seqbuff := substr(comments,position,basesize);
         seqbuff := seqbuff || chr(10);
         strbuff := strbuff||seqbuff;
         position := position + 68;
         if (position < length(comments)) then
            seqbuff := lpad(' ',12,' ');
            strbuff := strbuff||seqbuff;
         end if;
      end loop;
   end if;*/

   -- ORIGIN
   seqbuff := 'ORIGIN      ';
   strbuff := strbuff||seqbuff;

   if (seqstr is not null) then
      -- <7-9 spaces base number> <6 groups of 10 bases>
      position := 1;
      basesize := 10;
      while (position <= seqlen) loop
         if (mod(position,60) = 1) then
            seqbuff := chr(10)||lpad(to_char(position,'FM99999999'),9,' ')||' ';
            strbuff := strbuff||seqbuff;
         end if;
         seqbuff := substr(seqstr,position,basesize);
         seqbuff := seqbuff || ' ';
         strbuff := strbuff||seqbuff;
         position := position + 10;
      end loop;
   end if;

   -- //
   seqbuff := chr(10)||'//'||chr(10);
   strbuff := strbuff||seqbuff;

   return strbuff;
END
$_$;


ALTER FUNCTION public.getgenbankrecord(character varying) OWNER TO agrbrdf;

--
-- Name: getgeneexpressionstudycharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getgeneexpressionstudycharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        studyobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from geneExpressionStudyFact 
      where geneExpressionStudy = studyobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getgeneexpressionstudycharfact(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getgeneidfromaccession(character varying, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getgeneidfromaccession(character varying, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
declare
   accession alias for $1;
   maxversion alias for $2;
   geneid int4;
begin
   select getAttributeFromAccession(accession, maxversion, 'geneid') into geneid;
   return geneid;
end;$_$;


ALTER FUNCTION public.getgeneidfromaccession(character varying, integer) OWNER TO agrbrdf;

--
-- Name: getgeneinfofromaccession(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getgeneinfofromaccession(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   argseq alias for $1;
   infotype alias for $2;
   sqlstmnt text;
   rec record;
   geneid integer;
   vartemp varchar;
begin
   geneid := null;
   select getGeneidFromAccession(argseq,20) into geneid;
   
   if geneid is not null then
      sqlstmnt = 'select ' || infotype || ' as infotype from gene_info where geneid = ' || to_char(geneid,'9999999999');
      --raise notice '%',sqlstmnt;
   
      FOR rec in EXECUTE sqlstmnt LOOP 
         if upper(infotype) = 'TAX_ID' then
            return to_char(rec.infotype,'9999999');
         elsif upper(infotype) = 'DESCRIPTION' then
            vartemp := rec.infotype;
            return vartemp;
         else
            return rec.infotype;
         end if;
         exit;
      END LOOP;
   end if;

   return null;

end;$_$;


ALTER FUNCTION public.getgeneinfofromaccession(character varying, character varying) OWNER TO agrbrdf;

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

--
-- Name: getgenesymbolslink(integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getgenesymbolslink(integer, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      symbolcursor refcursor;
      geneobid ALIAS for $1;
      linktype ALIAS for $2;
      genesymbol varchar;
      resultlink varchar;
      myquote varchar;
      myplus varchar;
   BEGIN   
      myquote := '%22';
      myplus := '';
      open symbolcursor for
        select otf.termname
        from
        predicatelink p join ontologytermfact otf on
        p.subjectob = geneobid and p.predicate = 'PROVIDES_NOMENCLATURE' and
        p.predicatecomment like 'Link to aliases%' and
        otf.ontologyob = p.objectob;

      fetch symbolcursor into genesymbol;
      if linktype = 'google scholar' then
         resultlink := 'http://scholar.google.com/scholar?btnG=Search+Scholar&as_occt=title&as_subj=bio&hl=en&safe=off&as_oq=';
         if not FOUND then
            resultlink = 'emptylink';
         else
	    while FOUND loop
                resultlink := resultlink || myplus || myquote || genesymbol || myquote ;
                myplus := '+';
                fetch symbolcursor into genesymbol;
            end loop;
         end if;
      else if linktype = 'or list' then
         resultlink := '';
         myquote := '';
         if not FOUND then
            resultlink = '';
         else
	    while FOUND loop
                resultlink := resultlink || myplus || myquote || genesymbol || myquote ;
                myplus := ' OR ';
                fetch symbolcursor into genesymbol;
            end loop;
         end if;
      end if;
      end if;
    
      close symbolcursor;

      return resultlink;
    END;
$_$;


ALTER FUNCTION public.getgenesymbolslink(integer, character varying) OWNER TO agrbrdf;

--
-- Name: getgenetictestfact2char(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getgenetictestfact2char(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        factid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from genetictestfact2 
      where genetictestfact = factid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getgenetictestfact2char(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getimportcharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getimportcharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        importobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from importfunctionfact 
      where importfunction = importobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getimportcharfact(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getlibrarycharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getlibrarycharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        libraryobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from biolibraryfact 
      where biolibraryob = libraryobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getlibrarycharfact(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getmiamecharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getmiamecharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        studyobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from miamefact 
      where microarraystudy = studyobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getmiamecharfact(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getmicroarrayobservationcharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getmicroarrayobservationcharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        observationobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from microarrayObservationFact 
      where microarrayObservation = observationobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getmicroarrayobservationcharfact(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getmicroarrayobservationnumfact(integer, character varying, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getmicroarrayobservationnumfact(integer, character varying, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        observationobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        mymissingvaluetoken ALIAS for $4;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select 
         CASE 
            WHEN trim(attributevalue) is null THEN mymissingvaluetoken
            WHEN length(trim(attributevalue)) = 0 THEN  mymissingvaluetoken
            ELSE trim(attributevalue)
         END 
      from microarrayObservationFact 
      where microarrayObservation = observationobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getmicroarrayobservationnumfact(integer, character varying, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getnewobid(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getnewobid() RETURNS integer
    LANGUAGE plpgsql
    AS $$
   declare 
      mycur refcursor;
      newob integer;
   begin
      open mycur for 
      select nextval('ob_obidseq');
      fetch mycur into newob;
      return newob;
   end;
$$;


ALTER FUNCTION public.getnewobid() OWNER TO agrbrdf;

--
-- Name: getobtypeid(character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getobtypeid(character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        argtable ALIAS for $1;
        resultobtype integer;
    BEGIN
        select into resultobtype obtypeid from obtype where upper(tablename) = upper(argtable) and isvirtual = false;
        if not FOUND then
           return NULL;
        else
           return resultobtype;
        end if;
    END;
$_$;


ALTER FUNCTION public.getobtypeid(character varying) OWNER TO agrbrdf;

--
-- Name: FUNCTION getobtypeid(character varying); Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON FUNCTION getobtypeid(character varying) IS 'This function returns the numeric typeid, given the name of the type';


--
-- Name: getobtypename(integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getobtypename(integer) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        argtypeid ALIAS for $1;
        resultobtype varchar;
    BEGIN
        select into resultobtype lower(tablename) from obtype where obtypeid = argtypeid;
        if not FOUND then
           return NULL;
        else
           return resultobtype;
        end if;
    END;
$_$;


ALTER FUNCTION public.getobtypename(integer) OWNER TO agrbrdf;

--
-- Name: FUNCTION getobtypename(integer); Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON FUNCTION getobtypename(integer) IS 'This function returns the name of a type , given its numeric typeid';


--
-- Name: getrefseqfromaccession(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getrefseqfromaccession(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   argseq alias for $1;
   reftype alias for $2;
   refseqcur refcursor;
   refresult varchar;
   arggeneid integer;
begin
   refresult := null;
   arggeneid := null;
   select getGeneidFromAccession(argseq,20) into arggeneid;
   if arggeneid is null then
      return argseq;
   else
      if reftype = 'mRNA' then
         open refseqcur for 
         select rna_nucleotide_accession from gene2accession where
         geneid = arggeneid and rna_nucleotide_accession like 'NM%';
      elsif reftype = 'protein' then
         open refseqcur for 
         select protein_accession from gene2accession where
         geneid = arggeneid and protein_accession like 'NP%';
      end if;

      fetch refseqcur into refresult;
      close refseqcur;

      if refresult is null then
         refresult := argseq;
      end if;

   end if;

   return refresult;

end;$_$;


ALTER FUNCTION public.getrefseqfromaccession(character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getrefseqfromgeneid(integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getrefseqfromgeneid(integer, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   arggeneid alias for $1;
   reftype alias for $2;
   refseqcur refcursor;
   refresult varchar;
begin
   refresult := null;
   if arggeneid is null then
      return null;
   else
      if reftype = 'mRNA' then
         open refseqcur for 
         select rna_nucleotide_accession from gene2accession where
         geneid = arggeneid and rna_nucleotide_accession like 'NM%';
      elsif reftype = 'protein' then
         open refseqcur for 
         select protein_accession from gene2accession where
         geneid = arggeneid and protein_accession like 'NP%';
      end if;

      fetch refseqcur into refresult;
      close refseqcur;

      if refresult is null then
         refresult := argseq;
      end if;

   end if;

   return refresult;

end;$_$;


ALTER FUNCTION public.getrefseqfromgeneid(integer, character varying) OWNER TO agrbrdf;

--
-- Name: getrefseqfromgeneid(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getrefseqfromgeneid(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   arggeneid alias for $1;
   reftype alias for $2;
   refseqcur refcursor;
   refresult varchar;
begin
   refresult := null;
   if arggeneid is null then
      return null;
   else
      if reftype = 'mRNA' then
         open refseqcur for 
         select rna_nucleotide_accession from gene2accession where
         geneid = arggeneid and rna_nucleotide_accession like 'NM%';
      elsif reftype = 'protein' then
         open refseqcur for 
         select protein_accession from gene2accession where
         geneid = arggeneid and protein_accession like 'NP%';
      end if;

      fetch refseqcur into refresult;
      close refseqcur;

   end if;

   return refresult;

end;$_$;


ALTER FUNCTION public.getrefseqfromgeneid(character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getsamplecharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getsamplecharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        sampleobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from biosamplefact 
      where biosampleob = sampleobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getsamplecharfact(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: getsearchresultlist(text, character varying, integer, character varying, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getsearchresultlist(text, character varying, integer, character varying, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   BEGIN
      return getSearchResultList($1, $2, $3, $4, $5,0,null);
   END;
$_$;


ALTER FUNCTION public.getsearchresultlist(text, character varying, integer, character varying, integer) OWNER TO agrbrdf;

--
-- Name: getsearchresultlist(text, character varying, integer, character varying, integer, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getsearchresultlist(text, character varying, integer, character varying, integer, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   BEGIN
      return getSearchResultList($1, $2, $3, $4, $5, $6,null);
   END;
$_$;


ALTER FUNCTION public.getsearchresultlist(text, character varying, integer, character varying, integer, integer) OWNER TO agrbrdf;

--
-- Name: getsearchresultlist(text, character varying, integer, character varying, integer, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getsearchresultlist(text, character varying, integer, character varying, integer, integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
    DECLARE
       obCursor refcursor;
       obCursor2 refcursor;
       obCursor3 refcursor;


       searchTextArg ALIAS FOR $1;
       userName ALIAS FOR $2;
       maxListSize ALIAS FOR $3;
       obTypeName ALIAS FOR $4;
       useOldLimit ALIAS FOR $5;
       argListID ALIAS FOR $6;
       argListName ALIAS FOR $7;

       elementCount integer;
       tempCount integer;
       listid integer;
       listitem integer;
       listitem2 integer;
       listitem3 integer;
       obvar1 integer;
       textvar1 varchar;
       listxreflsid varchar;
       listxreflsid2 varchar;
       listxreflsid3 varchar;
       listcomment varchar;
       listcomment2 varchar;
       listcomment3 varchar;
       signature text;
       wildCardChar varchar;
       dollarChar varchar;
       searchText varchar;
       --existingListID varchar; new version of postgres strict
       existingListID integer;
       sensitivity integer;
    BEGIN
       -- ********** hard-coded PARAMETERS ************ ---
       sensitivity := 1;  -- use 2 or 3 for SG **** set this via arg list at some point ****

       -- locals 
       elementCount := 0;
       wildCardChar := '%';
       /* dollarChar := '$'; */

       searchText := searchTextArg;

       -- if the user has provided a wildcard , do not insert one ourselves - also , support * wildcard
       if position('*' in searchText) > 0 then
          searchText := translate(searchText,'*',wildCardChar);
       end if;
       if position(wildCardChar in searchText) > 0  then
          wildCardChar := '';
       end if;

       existingListID := argListID;
       if existingListID is null then
          existingListID  := 0;
       end if;



       -- check if there is an existing list with the same signature, if useOldLimit >= 0, and if we have not been given an existing list to update
       /* signature := searchText || dollarChar || maxListSize || dollarChar || obTypeName; */
       signature = 'Search of ' || obTypeName || ' for ' || searchText || ' (limited to first ' || maxListSize || ' hits)';

       if upper(obTypeName) != 'PAST SEARCHES' and upper(obTypeName) != 'COMMENTS' and upper(obTypeName) != 'EXTERNAL LINKS' 
                      and upper(obTypeName) != 'DATA FILES SUBMITTED' and useOldLimit >= 0 and existingListID = 0 then
          select obid into listid from oblist where listdefinition = signature and statuscode > 0;
       end if;

       if (not FOUND ) or  not (upper(obTypeName) != 'PAST SEARCHES' and upper(obTypeName) != 'COMMENTS' and upper(obTypeName) != 'EXTERNAL LINKS' 
                      and upper(obTypeName) != 'DATA FILES SUBMITTED' and useOldLimit >= 0 and existingListID = 0 ) then
          if existingListID = 0 then
              -- create the list 
             open obCursor for select nextval('ob_obidseq');
             fetch obCursor into listid;
             close obCursor; 

             if argListName is not null then 
                signature := argListName;
             end if;
             

             insert into obList(obid,listName,listType,listDefinition,xreflsid,maxMembership,createdBy,displayurl)
             /* values(listid,'Search hits : ' || obTypeName ,'SEARCH_RESULT', searchText || dollarChar || maxListSize || dollarChar || obTypeName,searchText || dollarChar || maxListSize || dollarChar || obTypeName, maxListSize, userName); */
             values(listid,'Search hits : ' || obTypeName ,'SEARCH_RESULT', signature,signature, maxListSize, userName,'search.gif');

          else
             listid = existingListID;
          end if;
       
    
          -- populate the list. For each type there is an ordering to ensure that 
          -- the most relevant objects occur first in the list. Each type may involve searches of 
          -- several different database fields


          --*************************************************************************
          --* search for genes                   
          --*
          --*************************************************************************
          --- searching for Genetic Objects
          -- note the changes to the "lsid" that is stored as part of the hit - this is cosmetic due
          -- to user request , they do not like the "geneticob." prefix
          if upper(obTypeName) = 'GENETIC TABLES' then

             -- if the search string does not contain a wildcard then first try to find an exact match on name 
             -- -  if we succeed then go no further
             -- first , name in gene table....
             if position(wildCardChar in searchText) = 0  then
                open obCursor for select obid , replace(xreflsid,'geneticob.','') , 
                coalesce(geneticobsymbols || ' '|| geneticobdescription ,
                         geneticobsymbols,
                         replace(xreflsid,'geneticob.','') || ' (symbol unknown)')
                from geneticob where lower(geneticobname) = lower(searchText);
                fetch obCursor into listitem, listxreflsid, listcomment;
                if FOUND then
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                end if;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- now try exact match on aliases
                if elementCount = 0 then               -- OK it must be 0 anyway but leave this in
                   open obCursor for select ontologyob from ontologytermfact where lower(termname) =
                   lower(searchText) and xreflsid like 'ontology.HOMOLOGENE_ALIASES%';
                   fetch obCursor into obvar1;
                   if elementCount < maxListSize and FOUND then
                      open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''), 
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                      from predicatelink pl join geneticob g on 
                      pl.subjectob = g.obid and pl.objectob = obvar1;
                      fetch obCursor2 into listitem,listxreflsid, listcomment;
                      close obCursor2;
                      if listitem is not null then
    	                 insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                         elementCount := elementCount + 1;
                      end if;
                   end if;
                   close obCursor;
                end if;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- now try exact match on sequences
                if elementCount = 0 then               -- OK it must be 0 anyway but leave this in
                   open obCursor for select obid from biosequenceob where sequencename  = searchText;
                   fetch obCursor into obvar1;
                   while elementCount < maxListSize and FOUND LOOP
                      open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),                         
			 coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                      from geneproductlink gpl join geneticob g on 
                      gpl.geneticob = g.obid and gpl.biosequenceob = obvar1;
                      fetch obCursor2 into listitem,listxreflsid, listcomment;
                      close obCursor2;
                      if listitem is not null then
    	                 insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                         elementCount := elementCount + 1;
                      end if;
                      fetch obCursor into obvar1;
                   end loop;
                   close obCursor;
                end if;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

             end if; -- no wildcards used - try exact match on names and return immediately if found


             -- add items whose name matches the query
             open obCursor for select obid , replace(xreflsid,'geneticob.','') , 
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
             from geneticob as g where lower(geneticobname) like lower(wildCardChar||searchText||wildCardChar)
                        or lower(geneticObSymbols) like lower(wildCardChar||searchText||wildCardChar) ; 
             fetch obCursor into listitem, listxreflsid, listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid, listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


             -- from here we only keep searching if there are not "enough" hits already.
             -- search the aliases ontology. Currently this code is somewhat too specific to 
             -- SGP but we may built gene indexes in general
             if elementCount < 5 then
                open obCursor for select ontologyob from ontologytermfact where lower(termname) like
                lower(wildCardChar||searchText||wildCardChar) and xreflsid like 'ontology.HOMOLOGENE_ALIASES%';
                fetch obCursor into obvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),
			 coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                   from predicatelink pl join geneticob g on 
                   pl.subjectob = g.obid and pl.objectob = obvar1;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;
                   close obCursor2;
                   if listitem is not null then
	              insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   end if;
                   fetch obCursor into obvar1;
                end loop;
                close obCursor;
             end if;



             -- search the titles ontology. Currently this code is somewhat too specific to 
             -- SGP but we may built gene indexes in general
             if elementCount < 15 then
                open obCursor for select ontologyob from ontologytermfact where lower(termname) like
                lower(wildCardChar||searchText||wildCardChar) and xreflsid like 'ontology.HOMOLOGENE_TITLES%';
                fetch obCursor into obvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                   from predicatelink pl join geneticob g on 
                   pl.subjectob = g.obid and pl.objectob = obvar1;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;
                   close obCursor2;
                   if listitem is not null then
	              insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   end if;
                   fetch obCursor into obvar1;
                end loop;
                close obCursor;
             end if;




             -- search the unigenes ontology. Currently this code is somewhat too specific to 
             -- SGP but we may built gene indexes in general
             if elementCount < 30 then
                open obCursor for select ontologyob from ontologytermfact where lower(termname) like
                lower(wildCardChar||searchText||wildCardChar) and xreflsid like 'ontology.HOMOLOGENE_UNIGENES%';
                fetch obCursor into obvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                   from predicatelink pl join geneticob g on 
                   pl.subjectob = g.obid and pl.objectob = obvar1;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;
                   close obCursor2;
                   if listitem is not null then
	              insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   end if;
                   fetch obCursor into obvar1;
                end loop;
                close obCursor;
             end if;



             -- search sequences. 
             if elementCount < 30 then
                open obCursor for select obid from biosequenceob where lower(sequencename) like
                lower(wildCardChar||searchText||wildCardChar) ;
                fetch obCursor into obvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                   from geneproductlink gpl join geneticob g on 
                   gpl.biosequenceob  = obvar1 and gpl.biosequenceob = obvar1;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;
                   close obCursor2;
                   if listitem is not null then
	              insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   end if;
                   fetch obCursor into obvar1;
                end loop;
                close obCursor;
             end if;



             -- next add items whose description matches the query. We now *do* insert wildcard, even if the user has submitted one
             wildCardChar := '%';
             if elementCount < maxListSize then
                open obCursor for select obid,replace(xreflsid,'geneticob.',''), 
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)') 
			 from geneticob as g where lower(geneticobdescription) like lower(wildCardChar||searchText||wildCardChar) or
                           lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar);
                fetch obCursor into listitem,listxreflsid,listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   fetch obCursor into listitem,listxreflsid, listcomment;
                   elementCount := elementCount + 1;
                end loop;
                close obCursor;
             end if; -- list not yet full


             -- next add items whose function description matches the query
             if elementCount < maxListSize then
                open obCursor for select distinct geneticob , replace(xreflsid,'geneticob.','') from geneticfunctionfact where lower(functioncomment) like lower(wildCardChar||searchText||wildCardChar);
                fetch obCursor into listitem,listxreflsid;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select  
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)') from geneticob as g where obid = listitem;
                   fetch obCursor2 into listcomment;
                   close obCursor2;
                   insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   fetch obCursor into listitem,listxreflsid,listcomment;
                   elementCount := elementCount + 1;
                end loop;
                close obCursor;
             end if; -- list not yet full

          --*************************************************************************
          --* search past searches                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'PAST SEARCHES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from oblist where listtype = 'SEARCH_RESULT' and lower(listdefinition) like lower(wildCardChar||searchText||wildCardChar); 
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;
         --*************************************************************************
          --* search gene lists                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'GENE LISTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from geneticoblist where listtype = 'USER_PROJECT_LIST' and 
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;
         --*************************************************************************
          --* search project lists                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'PROJECT LISTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from oblist where listtype = 'USER_PROJECT_LIST' and 
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search data source lists
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATASOURCE LISTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,listname from datasourcelist where
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(listcomment) like lower(wildCardChar||searchText||wildCardChar) or 
             lower(listname) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search sample lists
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'SAMPLE LISTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,listname from biosamplelist where
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(listcomment) like lower(wildCardChar||searchText||wildCardChar) or
             lower(listname) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

         --*************************************************************************
          --* search data source lists
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATA FORMS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,listname from datasourcelist where
             listtype = 'Data Form' and
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(listcomment) like lower(wildCardChar||searchText||wildCardChar) or 
             lower(listname) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search subject cohorts
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'SUBJECT LISTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from oblist where listtype = 'BIOSUBJECT_LIST' and 
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;



         --*************************************************************************
          --* search microarray series 
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'MICROARRAY SERIES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from oblist where listtype = 'MICROARRAY_SERIES_LIST' and 
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search protocols                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'PROTOCOLS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from bioprotocolob where
             lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(protocolname) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar) or
             lower(protocoltype ) like lower(wildCardChar||searchText||wildCardChar) or
             lower(protocoldescription ) like lower(wildCardChar||searchText||wildCardChar) or
             lower(protocoltext ) like lower(wildCardChar||searchText||wildCardChar);
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search analysis procedures                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'ANALYSIS PROCEDURES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from analysisprocedureob where
             lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(procedurename) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar) or
             lower(proceduretype ) like lower(wildCardChar||searchText||wildCardChar) or
             lower(proceduredescription ) like lower(wildCardChar||searchText||wildCardChar) or
             lower(sourcecode ) like lower(wildCardChar||searchText||wildCardChar);
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search import procedures                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'IMPORT PROCEDURES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from importprocedureob where
             lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(procedurename) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar) or
             lower(procedurecomment ) like lower(wildCardChar||searchText||wildCardChar) or
             lower(sourcecode ) like lower(wildCardChar||searchText||wildCardChar);
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for data files submitted                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATA FILES SUBMITTED' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,coalesce(
                          datasourcetype || '(' || datasupplier || ' , ' || datasourcecomment|| ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || datasupplier || ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || to_char(createddate,'dd-mm-yyyy') || ')')
                      from datasourceob where ( lower(physicalsourceuri) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(datasourcetype) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(datasourcename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or (lower(createdby) like lower(wildCardChar||searchText||wildCardChar)) 
                      or (lower(datasupplier) like lower(wildCardChar||searchText||wildCardChar))  );
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment,voptypeid) values (listid,listitem,listxreflsid,listcomment,29);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for data files imported                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATA FILES IMPORTED' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,coalesce(
                          datasourcetype || '(' || datasupplier || ' , ' || datasourcecomment|| ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || datasupplier || ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || to_char(createddate,'dd-mm-yyyy') || ')')
                      from datasourceob where ( lower(physicalsourceuri) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(datasourcetype) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(datasourcename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or (lower(createdby) like lower(wildCardChar||searchText||wildCardChar)) 
                      or (lower(datasupplier) like lower(wildCardChar||searchText||wildCardChar)) ) and exists
                      (select obid from importfunction where datasourceob = datasourceob.obid);
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment,voptypeid) values (listid,listitem,listxreflsid,listcomment,29);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for contributed data tables                 
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'CONTRIBUTED DATA TABLES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,coalesce(
                          datasourcetype || '(' || datasupplier || ' , ' || datasourcecomment|| ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || datasupplier || ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || to_char(createddate,'dd-mm-yyyy') || ')')
                      from datasourceob where datasourcetype = 'Contributed Database Table' and  ( 
                         lower(physicalsourceuri) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasupplier) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcename) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcecomment) like lower(wildCardChar||searchText||wildCardChar) 
                      );
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for data sources that are SQL queries                 
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'SQL QUERIES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,coalesce(
                          datasourcetype || '(' || datasupplier || ' , ' || datasourcecomment|| ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || datasupplier || ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || to_char(createddate,'dd-mm-yyyy') || ')')
                      from datasourceob where datasourcetype = 'SQL' and  ( 
                         lower(physicalsourceuri) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasupplier) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcecomment) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcename) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcecontent) like lower(wildCardChar||searchText||wildCardChar) 
                      );
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;



          --*************************************************************************
          --* search for data sources that are form elements
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'FORM ELEMENTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,coalesce(
                          datasourcetype || '(' || datasupplier || ' , ' || datasourcecomment|| ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || datasupplier || ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || to_char(createddate,'dd-mm-yyyy') || ')')
                      from datasourceob where datasourcetype = 'Form Element' and  ( 
                         lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasupplier) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcecomment) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcename) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcecontent) like lower(wildCardChar||searchText||wildCardChar) 
                      );
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for workflows                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'WORK FLOWS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from workflowob where ( lower(workflowdescription) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;
          --*************************************************************************
          --* search for workflowstages                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'WORK FLOW STAGES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from workflowstageob where ( lower(workflowstagedescription) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;
          --*************************************************************************
          --* search for microarray experiments                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'MICROARRAY EXPERIMENTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from geneexpressionstudy where
                   lower(studytype) like '%microarray%' and (
                   ( lower(xreflsid) like  lower(wildCardChar||searchText||wildCardChar))
                or ( lower(obkeywords) like lower(wildCardChar || searchText || wildCardChar))
                or ( lower(studydescription) like lower(wildCardChar || searchText || wildCardChar)));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search for genotype experiments                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'GENOTYPE EXPERIMENTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from genotypestudy where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(studytype) like lower(wildCardChar||searchText||wildCardChar)) 
		      or ( lower(obkeywords) like lower(wildCardChar || searchText || wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

         --*************************************************************************
          --* search for phenotype studies                    
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'PHENOTYPE STUDIES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from phenotypestudy where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
		      or ( lower(obkeywords) like lower(wildCardChar || searchText || wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search for genetic tests                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'GENETIC TESTS' then

             if position(wildCardChar in searchText) = 0  then
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| testdescription ,xreflsid)
                from genetictestfact where accession = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- no hit - try wildcard 
                open obCursor for select obid,xreflsid,
                coalesce(xreflsid  || ' '|| testdescription ,xreflsid) 
                from genetictestfact where lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar);
                fetch obCursor into listitem,listxreflsid;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
             else
                open obCursor for select obid,xreflsid from genetictestfact where lower(xreflsid) like lower(searchText);
                fetch obCursor into listitem,listxreflsid;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
             end if;
             close obCursor;

         --*************************************************************************
          --* search for genetic test runs                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'GENETIC TEST RUNS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from genotypeobservation where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(genotypeobserved) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(genotypeobserveddescription) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(finalgenotype) like lower(wildCardChar||searchText||wildCardChar)) 
		      or ( lower(finalgenotypedescription) like lower(wildCardChar || searchText || wildCardChar))
		      or ( lower(observationcomment) like lower(wildCardChar || searchText || wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for biosubjects                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'BIOSUBJECTS' then
             -- add items whose name matches the query exactly
             tempCount := 0;
             open obCursor for select obid,xreflsid from biosubjectob where ( xreflsid = searchText) ;
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
                tempCount := tempCount + 1;
             end loop;
             close obCursor;

             -- if we got any exact matches , stop there, else search other fields
             if tempCount = 0 then
                open obCursor for select obid,xreflsid from biosubjectob where ( lower(xreflsid) like  lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(subjectspeciesname) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(subjectdescription) like lower(wildCardChar||searchText||wildCardChar));
                fetch obCursor into listitem,listxreflsid;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                   fetch obCursor into listitem,listxreflsid;
                   elementCount := elementCount + 1;
                end loop;
                close obCursor;
             end if;

          --*************************************************************************
          --* search for biosamples                 
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'BIOSAMPLES' then
             open obCursor for select obid,xreflsid from biosampleob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(samplename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(sampledescription) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(samplestorage) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for batches
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'BATCHES' then
             open obCursor for select obid,xreflsid from batchob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(batchname) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(batchdescription) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(batchtype) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;



          --*************************************************************************
          --* search for biolibraries
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'LIBRARIES' then
             open obCursor for select obid,xreflsid from biolibraryob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(libraryname) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(librarydescription) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(librarystorage) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for library sequencing
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'LIBRARY SEQUENCING' then
             open obCursor for select obid,xreflsid from librarysequencingfunction where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(runby) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(functioncomment) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for biosampling                 
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'BIOSAMPLING' then
             open obCursor for select obid,xreflsid from biosamplingfunction where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(samplingcomment) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for ontologies                
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'ONTOLOGIES' then
             open obCursor for select obid,xreflsid from ontologyob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(ontologydescription) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for ontology terms
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'ONTOLOGY TERMS' then
             -- if no wildcards try an exact match on the term
             if position(wildCardChar in searchText) = 0  then
                open obCursor for select obid , xreflsid , 
                coalesce(termname || ' '|| termdescription ,termname)
                from ontologytermfact where termname = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   fetch obCursor into listitem,listxreflsid, listcomment;
                   elementCount := elementCount + 1;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;
             end if;
             

             -- now try wildcard search (i.e. either they used wildcards or no hits yet)
             open obCursor for select obid,xreflsid,
                    coalesce(termname || ' '|| termdescription ,termname)
                    from ontologytermfact where lower(termname) like lower(wildCardChar||searchText||wildCardChar);

             fetch obCursor into listitem,listxreflsid,listcomment;

             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;

             close obCursor;
             if elementCount > 0 then
                update oblist set currentmembership = elementCount where obid = listid;
                return listid;
             end if;

             -- still no hit - try description and unitname
             open obCursor for select obid,xreflsid,
                    coalesce(termname || ' '|| termdescription ,termname)
                    from ontologytermfact where ( lower(termdescription) like lower(wildCardChar||searchText||wildCardChar))
                   or ( lower(unitname) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;

             close obCursor;

          --*************************************************************************
          --* search for databases
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATABASES' then
             open obCursor for select obid,xreflsid from biodatabaseob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(databasename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(databasedescription) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for database search runs
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATABASE SEARCHES' then
             open obCursor for select obid, xreflsid, coalesce(xreflsid  || ' : '|| studydescription ,xreflsid)  from databasesearchstudy 
             where lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) ;
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for lab resources
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'ALL LAB RESOURCES' then
             open obCursor for select obid,xreflsid from labresourceob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(resourcename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(resourcedescription) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(resourcetype) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(supplier) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for microarrays
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'MICROARRAYS' then
             open obCursor for select obid,xreflsid from labresourceob where resourcetype = 'microarray' and (( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(resourcename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(resourcedescription) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(supplier) like lower(wildCardChar||searchText||wildCardChar)));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for comments
          --*
          --*************************************************************************
          elsif upper(obTypeName) = 'COMMENTS' then
             open obCursor for select obid,xreflsid from commentob where ( lower(createdby) like lower(searchText)) 
                      or ( lower(commentstring) like lower(wildCardChar||searchText||wildCardChar)) ;
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for uri
          --*
          --*************************************************************************
          elsif upper(obTypeName) = 'EXTERNAL LINKS' then
             open obCursor for select obid,xreflsid from uriob where ( lower(createdby) like lower(searchText)) 
                      or ( lower(uristring) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(uricomment) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for biosequences              
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'BIOSEQUENCES' then



             -- if the search string does not contain a wildcard then first try to find an exact match on name 
             -- -  if we succeed then go no further
             -- first , name in sequence table....
             if position(wildCardChar in searchText) = 0  then
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                from biosequenceob where sequencename = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

               -- try lsid
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                from biosequenceob where xreflsid = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;


               -- try sequencename with .ab1 suffix
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                from biosequenceob where sequencename = searchText||'.ab1';
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;


                -- try splitting the sequecename name using an underscore character and using the second
                -- token as the sequence name (this is an adhoc rule used in some sequence databases , where there
                -- is a species or breed prefix. It probably should be shifted to a site-specific 
                -- search engine function
                if split_part(searchText,'_',2) is not null then
                   open obCursor for select obid , xreflsid, 
                   coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                   from biosequenceob where sequencename = split_part(searchText,'_',2);
                   fetch obCursor into listitem, listxreflsid, listcomment;
                   if FOUND then
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   end if;
                   close obCursor;

                   if elementCount > 0 then
                      update oblist set currentmembership = elementCount where obid = listid;
                      return listid;
                   end if;
                end if;

                -- if the search string is <= 5 characters this looks like a list name - try searching 
                -- for a sequence list 



             end if; -- no wildcards used - try exact match on names and return immediately if found


       


             --- from here , attempt wildcard matches on description and other fields -------




             -- add seqs that had blast hits to matching descriptions. 
             open obCursor for select obid,xreflsid , 
                ' ( hit to : ' || coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid) || ')'
                      from biosequenceob where ( lower(sequencedescription) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid, listcomment;
             while elementCount < maxListSize and FOUND LOOP
                open obCursor2 for select  
                querysequence from databasesearchobservation where hitsequence = listitem;
                fetch obCursor2 into listitem2;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor3 for select obid , xreflsid, 
                   coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                   from biosequenceob where obid = listitem2 and not exists
                   (select ob from listmembershiplink where oblist = listid and
                   ob = listitem2);
                   fetch obCursor3 into listitem3,listxreflsid3, listcomment3;
                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem3,listxreflsid3,listcomment);
                      fetch obCursor3 into listitem3,listxreflsid3, listcomment3;
                      elementCount := elementCount + 1;
                   end loop;
                   close obCursor3;
                   fetch obCursor2 into listitem2;
                end loop;
                close obCursor2;
                fetch obCursor into listitem,listxreflsid,listcomment;
             end loop;
             close obCursor;


             -- next add the seqs that had matching descriptions
	     if elementCount < maxListSize then
                open obCursor for select obid,xreflsid , 
                   coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid) 
                         from biosequenceob where ( lower(sequencedescription) like lower(wildCardChar||searchText||wildCardChar)) and
                         not exists 
                         (select ob from listmembershiplink where oblist = listid and
                         ob = biosequenceob.obid);             
                fetch obCursor into listitem,listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   fetch obCursor into listitem,listxreflsid,listcomment;
                   elementCount := elementCount + 1;
                end loop;
                close obCursor;
             end if;


             -- try wildcard on lsid
             open obCursor for select obid , xreflsid, 
             coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
             from biosequenceob where lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar);
             fetch obCursor into listitem, listxreflsid, listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                elementCount := elementCount + 1;
                fetch obCursor into listitem,listxreflsid, listcomment;
             end loop;
             close obCursor;


	     -- next add items from the seqfeaturefact table
             if sensitivity >= 3 then
	        if elementCount < maxListSize then
                   open obCursor for select distinct biosequenceob ,xreflsid  from biosequencefeaturefact f where 
                   f.featuretype = lower(searchText);
                   fetch obCursor into listitem,listxreflsid;
                   while elementCount < maxListSize and FOUND LOOP
                      open obCursor2 for select  
                      coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid) from biosequenceob where obid = listitem;
                      fetch obCursor2 into listcomment;
                      close obCursor2;
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      fetch obCursor into listitem,listxreflsid,listcomment;
                      elementCount := elementCount + 1;
                   end loop;
                   close obCursor;
                end if;
             end if;


             -- search gene ontology links
             --if elementCount < 30 then
             --   open obCursor for select ontologyob from ontologytermfact where lower(termname) like
             --   lower(wildCardChar||searchText||wildCardChar) and xreflsid like 'ontology.GO%';
             --   fetch obCursor into obvar1;
             --   while elementCount < maxListSize and FOUND LOOP
             --      open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),
             --            coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
             --            g.geneticobsymbols,
             --            replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
             --      from predicatelink pl join geneticob g on 
             --      pl.subjectob = g.obid and pl.objectob = obvar1;
             --      fetch obCursor2 into listitem,listxreflsid, listcomment;
             --      close obCursor2;
             --      if listitem is not null then
	     --         insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
             --         elementCount := elementCount + 1;
             --      end if;
             --      fetch obCursor into obvar1;
             --   end loop;
             --   close obCursor;
             --end if;



	     -- add sequences that are the gene products of genes that match the query - would
             -- be nice to do this recursively by a call to this method but this doesnt work
             -- (of course). The following code basically takes the above code for locating genes, 
             -- and joins to the geneproduct table

             -- **************** this was OK in SG which had a gene index but probably just slows down other 
             -- **************** instances. Perhaps we need to pass specific sensitivity and specificity hints to 
             -- **************** this method so we can control this. In the meantime I have stuck an internal 
             -- **************** sensitivity variable at the top
           
             if sensitivity >= 2 then

                -- first add items whose gene name matches the query
   	        if elementCount < maxListSize then
                   open obCursor for select gpl.biosequenceob , gpl.xreflsid from geneproductlink gpl, geneticob go where 
                   (lower(go.geneticobname) like lower(wildCardChar||searchText||wildCardChar)
                   or lower(go.geneticObSymbols) like lower(wildCardChar||searchText||wildCardChar)) and
                   gpl.geneticob = go.obid ; 
                   fetch obCursor into listitem,listxreflsid;
                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                      fetch obCursor into listitem,listxreflsid;
                      elementCount := elementCount + 1;
                   end loop;
                   close obCursor;
                end if;


                -- next add items whose description matches the query
                if elementCount < maxListSize then
                   open obCursor for select gpl.biosequenceob , gpl.xreflsid from geneproductlink gpl, geneticob go where 
                   (lower(go.geneticobdescription) like lower(wildCardChar||searchText||wildCardChar) or
                              lower(go.obkeywords) like lower(wildCardChar||searchText||wildCardChar)) and
                    gpl.geneticob = go.obid ;  
                   fetch obCursor into listitem,listxreflsid;
                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                      fetch obCursor into listitem,listxreflsid;
                      elementCount := elementCount + 1;
                   end loop;
                   close obCursor;
                end if; -- list not yet full


                -- add items whose function description matches the query
                if elementCount < maxListSize then
                   open obCursor for select distinct gpl.biosequenceob , gpl.xreflsid from geneproductlink gpl, geneticfunctionfact gff 
                   where lower(gff.functioncomment) like  lower(wildCardChar||searchText||wildCardChar) and
                   gpl.geneticob = gff.geneticob ;
                   fetch obCursor into listitem,listxreflsid;
                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                      fetch obCursor into listitem,listxreflsid;
                      elementCount := elementCount + 1;
                   end loop;
                   close obCursor;
                end if; -- list not yet full
             end if; -- sensitivity >= 2




          --*************************************************************************
          --* search for microarray spots                    
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'MICROARRAY SPOTS' then

             -- the strategy is currently as follows
             -- Exact matches (1) : 
             -- 1. Accession 
             -- 3. Gal_id
             -- 4. gal_name
             -- 5. xreflsid

             -- exact matches (2) :
             -- GO ontology on termname then link via GO association and sequence association


             -- exact matches (3) :
             -- biosequence on sequencename then link via sequence-spot link


             -- exact matches (4) , retrieve all records
             -- biosequence  on sequencename then link via blast hit

             -- wild cards or not hit yet :

       
             -- xreflsid
             -- accession
             -- spot description
             -- GO term description then link via GO association and sequence association
             -- sequence description then link via blast hits 



             -- if the search string does not contain a wildcard then first try to find an exact match on accession and 
             -- xreflsid before going any further
             if position(wildCardChar in searchText) = 0  then
                -- accession
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                from microarrayspotfact where accession = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- gal_id
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                from microarrayspotfact where gal_id = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- gal_name
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                from microarrayspotfact where gal_name = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- xreflsid
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                from microarrayspotfact where xreflsid = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;


                -- exact match on a sequencename (e.g. NCBI) , then via database hit and sequence association
                open obCursor for select obid, sequencedescription 
                from biosequenceob where sequencename = searchText;
                fetch obCursor into obvar1, textvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select msf.obid, msf.xreflsid, coalesce(msf.accession || ' ' || msf.gal_description || ' ' || textvar1,
                         msf.accession || ' ' || textvar1)  
                      from (databasesearchobservation dso join predicatelink plsa on 
                      dso.hitsequence = obvar1 and 
                      plsa.objectob = dso.querysequence and plsa.predicate = 'ARRAYSPOT-SEQUENCE') join
                      microarrayspotfact msf on msf.obid = plsa.subjectob ;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;

                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                      fetch obCursor2 into listitem, listxreflsid, listcomment;
                   end loop;
                   close obCursor2;

                   fetch obCursor into obvar1, textvar1;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;                





                -- exact match on go term via go association and sequence association
                open obCursor for select obid 
                from ontologytermfact where termname = searchText;
                fetch obCursor into obvar1;
                if elementCount < maxListSize and FOUND then
                   open obCursor2 for select msf.obid, msf.xreflsid, coalesce(msf.accession || ' ' || msf.gal_description,
                         msf.accession)  
                      from (predicatelink plgo join predicatelink plsa on 
                      plgo.objectob = obvar1 and plgo.predicate = 'GO_ASSOCIATION' and 
                      plsa.objectob = plgo.subjectob and plsa.predicate = 'ARRAYSPOT-SEQUENCE') join
                      microarrayspotfact msf on msf.obid = plsa.subjectob ;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;

                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                      fetch obCursor2 into listitem, listxreflsid, listcomment;
                   end loop;
                   close obCursor2;
                end if;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;
             end if;

             ---------------------------------------------------------
             ---- either no exact matches or wildcards were specified
             ---------------------------------------------------------


             -- first try items whose xreflsid can match the query
             open obCursor for select obid,xreflsid,coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                  from microarrayspotfact where lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar); 
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

             -- if some hits on xreflsid were found, they are not searching using
             -- keywords, we can exit
             if elementCount > 0 then
                update oblist set currentmembership = elementCount where obid = listid;
                return listid;
             end if;


             -- next try items whose accession can match the query
             open obCursor for select obid,xreflsid,coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                  from microarrayspotfact where lower(accession) like lower(wildCardChar||searchText||wildCardChar); 
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


             -- next try items whose description can match the query
             open obCursor for select obid,xreflsid,coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                  from microarrayspotfact where lower(gal_description) like lower(wildCardChar||searchText||wildCardChar); 
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


             -- match go term via description and link via go association and sequence association
             if elementCount < maxListSize then
                open obCursor for select obid , termname || ' ' || termdescription
                from ontologytermfact where lower(termdescription) like lower(wildCardChar||searchText||wildCardChar);
                fetch obCursor into obvar1,textvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select msf.obid, msf.xreflsid, coalesce(msf.accession || ' ' || msf.gal_description || ' ' || textvar1,
                         msf.accession || ' ' || textvar1)  
                      from (predicatelink plgo join predicatelink plsa on 
                      plgo.objectob = obvar1 and plgo.predicate = 'GO_ASSOCIATION' and 
                      plsa.objectob = plgo.subjectob and plsa.predicate = 'ARRAYSPOT-SEQUENCE') join
                      microarrayspotfact msf on msf.obid = plsa.subjectob ;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;

                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                      fetch obCursor2 into listitem, listxreflsid, listcomment;
                   end loop;
                   close obCursor2;

                   fetch obCursor into obvar1,textvar1;
                end loop;
                close obCursor;

                -- if we got some hits using GO that will do
                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;
             end if;



             -- match sequence description , then via database hit and sequence association
             if elementCount < maxListSize then
                open obCursor for select obid, sequencedescription 
                from biosequenceob where lower(sequencedescription) like lower(wildCardChar||searchText||wildCardChar);
                fetch obCursor into obvar1, textvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select msf.obid, msf.xreflsid, coalesce(msf.accession || ' ' || msf.gal_description || ' ' || textvar1,
                         msf.accession || ' ' || textvar1)  
                      from (databasesearchobservation dso join predicatelink plsa on 
                      dso.hitsequence = obvar1 and 
                      plsa.objectob = dso.querysequence and plsa.predicate = 'ARRAYSPOT-SEQUENCE') join
                      microarrayspotfact msf on msf.obid = plsa.subjectob ;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;

                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                      fetch obCursor2 into listitem, listxreflsid, listcomment;
                   end loop;
                   close obCursor2;

                   fetch obCursor into obvar1, textvar1;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;                
             end if;


          --*************************************************************************
          --* else do a basic search                   
          --*
          --*************************************************************************

          else 
             open obCursor for select obid,xreflsid from ob where obkeywords like lower(wildCardChar||searchText||wildCardChar);
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;
          end if;


          -- finally , update the membership count of the list
          update oblist set currentmembership = currentmembership + elementCount where obid = listid;
       end if; -- no existing list could be re-used

       return listid;

    END;
$_$;


ALTER FUNCTION public.getsearchresultlist(text, character varying, integer, character varying, integer, integer, character varying) OWNER TO agrbrdf;

--
-- Name: getsearchresultlisttest(text, character varying, integer, character varying, integer, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getsearchresultlisttest(text, character varying, integer, character varying, integer, integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
    DECLARE
       obCursor refcursor;
       obCursor2 refcursor;
       obCursor3 refcursor;


       searchTextArg ALIAS FOR $1;
       userName ALIAS FOR $2;
       maxListSize ALIAS FOR $3;
       obTypeName ALIAS FOR $4;
       useOldLimit ALIAS FOR $5;
       argListID ALIAS FOR $6;
       argListName ALIAS FOR $7;

       elementCount integer;
       tempCount integer;
       listid integer;
       listitem integer;
       listitem2 integer;
       listitem3 integer;
       obvar1 integer;
       textvar1 varchar;
       listxreflsid varchar;
       listxreflsid2 varchar;
       listxreflsid3 varchar;
       listcomment varchar;
       listcomment2 varchar;
       listcomment3 varchar;
       signature text;
       wildCardChar varchar;
       dollarChar varchar;
       searchText varchar;
       --existingListID varchar; new version of postgres strict
       existingListID integer;
       sensitivity integer;
    BEGIN
       -- ********** hard-coded PARAMETERS ************ ---
       sensitivity := 1;  -- use 2 or 3 for SG **** set this via arg list at some point ****

       -- locals 
       elementCount := 0;
       wildCardChar := '%';
       /* dollarChar := '$'; */

       searchText := searchTextArg;

       -- if the user has provided a wildcard , do not insert one ourselves - also , support * wildcard
       if position('*' in searchText) > 0 then
          searchText := translate(searchText,'*',wildCardChar);
       end if;
       if position(wildCardChar in searchText) > 0  then
          wildCardChar := '';
       end if;

       existingListID := argListID;
       if existingListID is null then
          existingListID  := 0;
       end if;



       -- check if there is an existing list with the same signature, if useOldLimit >= 0, and if we have not been given an existing list to update
       /* signature := searchText || dollarChar || maxListSize || dollarChar || obTypeName; */
       signature = 'Search of ' || obTypeName || ' for ' || searchText || ' (limited to first ' || maxListSize || ' hits)';

       if upper(obTypeName) != 'PAST SEARCHES' and upper(obTypeName) != 'COMMENTS' and upper(obTypeName) != 'EXTERNAL LINKS' 
                      and upper(obTypeName) != 'DATA FILES SUBMITTED' and useOldLimit >= 0 and existingListID = 0 then
          select obid into listid from oblist where listdefinition = signature and statuscode > 0;
       end if;

       if (not FOUND ) or  not (upper(obTypeName) != 'PAST SEARCHES' and upper(obTypeName) != 'COMMENTS' and upper(obTypeName) != 'EXTERNAL LINKS' 
                      and upper(obTypeName) != 'DATA FILES SUBMITTED' and useOldLimit >= 0 and existingListID = 0 ) then
          if existingListID = 0 then
              -- create the list 
             open obCursor for select nextval('ob_obidseq');
             fetch obCursor into listid;
             close obCursor; 

             if argListName is not null then 
                signature := argListName;
             end if;
             

             insert into obList(obid,listName,listType,listDefinition,xreflsid,maxMembership,createdBy,displayurl)
             /* values(listid,'Search hits : ' || obTypeName ,'SEARCH_RESULT', searchText || dollarChar || maxListSize || dollarChar || obTypeName,searchText || dollarChar || maxListSize || dollarChar || obTypeName, maxListSize, userName); */
             values(listid,'Search hits : ' || obTypeName ,'SEARCH_RESULT', signature,signature, maxListSize, userName,'search.gif');

          else
             listid = existingListID;
          end if;
       
    
          -- populate the list. For each type there is an ordering to ensure that 
          -- the most relevant objects occur first in the list. Each type may involve searches of 
          -- several different database fields


          --*************************************************************************
          --* search for genes                   
          --*
          --*************************************************************************
          --- searching for Genetic Objects
          -- note the changes to the "lsid" that is stored as part of the hit - this is cosmetic due
          -- to user request , they do not like the "geneticob." prefix
          if upper(obTypeName) = 'GENETIC TABLES' then

             -- if the search string does not contain a wildcard then first try to find an exact match on name 
             -- -  if we succeed then go no further
             -- first , name in gene table....
             if position(wildCardChar in searchText) = 0  then
                open obCursor for select obid , replace(xreflsid,'geneticob.','') , 
                coalesce(geneticobsymbols || ' '|| geneticobdescription ,
                         geneticobsymbols,
                         replace(xreflsid,'geneticob.','') || ' (symbol unknown)')
                from geneticob where lower(geneticobname) = lower(searchText);
                fetch obCursor into listitem, listxreflsid, listcomment;
                if FOUND then
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                end if;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- now try exact match on aliases
                if elementCount = 0 then               -- OK it must be 0 anyway but leave this in
                   open obCursor for select ontologyob from ontologytermfact where lower(termname) =
                   lower(searchText) and xreflsid like 'ontology.HOMOLOGENE_ALIASES%';
                   fetch obCursor into obvar1;
                   if elementCount < maxListSize and FOUND then
                      open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''), 
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                      from predicatelink pl join geneticob g on 
                      pl.subjectob = g.obid and pl.objectob = obvar1;
                      fetch obCursor2 into listitem,listxreflsid, listcomment;
                      close obCursor2;
                      if listitem is not null then
    	                 insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                         elementCount := elementCount + 1;
                      end if;
                   end if;
                   close obCursor;
                end if;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- now try exact match on sequences
                if elementCount = 0 then               -- OK it must be 0 anyway but leave this in
                   open obCursor for select obid from biosequenceob where sequencename  = searchText;
                   fetch obCursor into obvar1;
                   while elementCount < maxListSize and FOUND LOOP
                      open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),                         
			 coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                      from geneproductlink gpl join geneticob g on 
                      gpl.geneticob = g.obid and gpl.biosequenceob = obvar1;
                      fetch obCursor2 into listitem,listxreflsid, listcomment;
                      close obCursor2;
                      if listitem is not null then
    	                 insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                         elementCount := elementCount + 1;
                      end if;
                      fetch obCursor into obvar1;
                   end loop;
                   close obCursor;
                end if;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

             end if; -- no wildcards used - try exact match on names and return immediately if found


             -- add items whose name matches the query
             open obCursor for select obid , replace(xreflsid,'geneticob.','') , 
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
             from geneticob as g where lower(geneticobname) like lower(wildCardChar||searchText||wildCardChar)
                        or lower(geneticObSymbols) like lower(wildCardChar||searchText||wildCardChar) ; 
             fetch obCursor into listitem, listxreflsid, listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid, listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


             -- from here we only keep searching if there are not "enough" hits already.
             -- search the aliases ontology. Currently this code is somewhat too specific to 
             -- SGP but we may built gene indexes in general
             if elementCount < 5 then
                open obCursor for select ontologyob from ontologytermfact where lower(termname) like
                lower(wildCardChar||searchText||wildCardChar) and xreflsid like 'ontology.HOMOLOGENE_ALIASES%';
                fetch obCursor into obvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),
			 coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                   from predicatelink pl join geneticob g on 
                   pl.subjectob = g.obid and pl.objectob = obvar1;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;
                   close obCursor2;
                   if listitem is not null then
	              insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   end if;
                   fetch obCursor into obvar1;
                end loop;
                close obCursor;
             end if;



             -- search the titles ontology. Currently this code is somewhat too specific to 
             -- SGP but we may built gene indexes in general
             if elementCount < 15 then
                open obCursor for select ontologyob from ontologytermfact where lower(termname) like
                lower(wildCardChar||searchText||wildCardChar) and xreflsid like 'ontology.HOMOLOGENE_TITLES%';
                fetch obCursor into obvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                   from predicatelink pl join geneticob g on 
                   pl.subjectob = g.obid and pl.objectob = obvar1;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;
                   close obCursor2;
                   if listitem is not null then
	              insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   end if;
                   fetch obCursor into obvar1;
                end loop;
                close obCursor;
             end if;




             -- search the unigenes ontology. Currently this code is somewhat too specific to 
             -- SGP but we may built gene indexes in general
             if elementCount < 30 then
                open obCursor for select ontologyob from ontologytermfact where lower(termname) like
                lower(wildCardChar||searchText||wildCardChar) and xreflsid like 'ontology.HOMOLOGENE_UNIGENES%';
                fetch obCursor into obvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                   from predicatelink pl join geneticob g on 
                   pl.subjectob = g.obid and pl.objectob = obvar1;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;
                   close obCursor2;
                   if listitem is not null then
	              insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   end if;
                   fetch obCursor into obvar1;
                end loop;
                close obCursor;
             end if;



             -- search sequences. 
             if elementCount < 30 then
                open obCursor for select obid from biosequenceob where lower(sequencename) like
                lower(wildCardChar||searchText||wildCardChar) ;
                fetch obCursor into obvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
                   from geneproductlink gpl join geneticob g on 
                   gpl.biosequenceob  = obvar1 and gpl.biosequenceob = obvar1;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;
                   close obCursor2;
                   if listitem is not null then
	              insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   end if;
                   fetch obCursor into obvar1;
                end loop;
                close obCursor;
             end if;



             -- next add items whose description matches the query. We now *do* insert wildcard, even if the user has submitted one
             wildCardChar := '%';
             if elementCount < maxListSize then
                open obCursor for select obid,replace(xreflsid,'geneticob.',''), 
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)') 
			 from geneticob as g where lower(geneticobdescription) like lower(wildCardChar||searchText||wildCardChar) or
                           lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar);
                fetch obCursor into listitem,listxreflsid,listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   fetch obCursor into listitem,listxreflsid, listcomment;
                   elementCount := elementCount + 1;
                end loop;
                close obCursor;
             end if; -- list not yet full


             -- next add items whose function description matches the query
             if elementCount < maxListSize then
                open obCursor for select distinct geneticob , replace(xreflsid,'geneticob.','') from geneticfunctionfact where lower(functioncomment) like lower(wildCardChar||searchText||wildCardChar);
                fetch obCursor into listitem,listxreflsid;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select  
                         coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
                         g.geneticobsymbols,
                         replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)') from geneticob as g where obid = listitem;
                   fetch obCursor2 into listcomment;
                   close obCursor2;
                   insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   fetch obCursor into listitem,listxreflsid,listcomment;
                   elementCount := elementCount + 1;
                end loop;
                close obCursor;
             end if; -- list not yet full

          --*************************************************************************
          --* search past searches                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'PAST SEARCHES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from oblist where listtype = 'SEARCH_RESULT' and lower(listdefinition) like lower(wildCardChar||searchText||wildCardChar); 
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;
         --*************************************************************************
          --* search gene lists                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'GENE LISTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from geneticoblist where listtype = 'USER_PROJECT_LIST' and 
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;
         --*************************************************************************
          --* search project lists                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'PROJECT LISTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from oblist where listtype = 'USER_PROJECT_LIST' and 
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search data source lists
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATASOURCE LISTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,listname from datasourcelist where
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(listcomment) like lower(wildCardChar||searchText||wildCardChar) or 
             lower(listname) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search sample lists
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'SAMPLE LISTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,listname from biosamplelist where
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(listcomment) like lower(wildCardChar||searchText||wildCardChar) or
             lower(listname) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

         --*************************************************************************
          --* search data source lists
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATA FORMS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,listname from datasourcelist where
             listtype = 'Data Form' and
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(listcomment) like lower(wildCardChar||searchText||wildCardChar) or 
             lower(listname) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search subject cohorts
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'SUBJECT LISTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from oblist where listtype = 'BIOSUBJECT_LIST' and 
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;



         --*************************************************************************
          --* search microarray series 
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'MICROARRAY SERIES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from oblist where listtype = 'MICROARRAY_SERIES_LIST' and 
             (lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search protocols                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'PROTOCOLS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from bioprotocolob where
             lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(protocolname) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar) or
             lower(protocoltype ) like lower(wildCardChar||searchText||wildCardChar) or
             lower(protocoldescription ) like lower(wildCardChar||searchText||wildCardChar) or
             lower(protocoltext ) like lower(wildCardChar||searchText||wildCardChar);
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search analysis procedures                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'ANALYSIS PROCEDURES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from analysisprocedureob where
             lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(procedurename) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar) or
             lower(proceduretype ) like lower(wildCardChar||searchText||wildCardChar) or
             lower(proceduredescription ) like lower(wildCardChar||searchText||wildCardChar) or
             lower(sourcecode ) like lower(wildCardChar||searchText||wildCardChar);
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search import procedures                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'IMPORT PROCEDURES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from importprocedureob where
             lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
             lower(procedurename) like lower(wildCardChar||searchText||wildCardChar) or
             lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar) or
             lower(procedurecomment ) like lower(wildCardChar||searchText||wildCardChar) or
             lower(sourcecode ) like lower(wildCardChar||searchText||wildCardChar);
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for data files submitted                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATA FILES SUBMITTED' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,coalesce(
                          datasourcetype || '(' || datasupplier || ' , ' || datasourcecomment|| ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || datasupplier || ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || to_char(createddate,'dd-mm-yyyy') || ')')
                      from datasourceob where ( lower(physicalsourceuri) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(datasourcetype) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(datasourcename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or (lower(createdby) like lower(wildCardChar||searchText||wildCardChar)) 
                      or (lower(datasupplier) like lower(wildCardChar||searchText||wildCardChar))  );
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment,voptypeid) values (listid,listitem,listxreflsid,listcomment,29);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for data files imported                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATA FILES IMPORTED' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,coalesce(
                          datasourcetype || '(' || datasupplier || ' , ' || datasourcecomment|| ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || datasupplier || ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || to_char(createddate,'dd-mm-yyyy') || ')')
                      from datasourceob where ( lower(physicalsourceuri) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(datasourcetype) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(datasourcename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or (lower(createdby) like lower(wildCardChar||searchText||wildCardChar)) 
                      or (lower(datasupplier) like lower(wildCardChar||searchText||wildCardChar)) ) and exists
                      (select obid from importfunction where datasourceob = datasourceob.obid);
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment,voptypeid) values (listid,listitem,listxreflsid,listcomment,29);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for contributed data tables                 
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'CONTRIBUTED DATA TABLES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,coalesce(
                          datasourcetype || '(' || datasupplier || ' , ' || datasourcecomment|| ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || datasupplier || ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || to_char(createddate,'dd-mm-yyyy') || ')')
                      from datasourceob where datasourcetype = 'Contributed Database Table' and  ( 
                         lower(physicalsourceuri) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasupplier) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcename) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcecomment) like lower(wildCardChar||searchText||wildCardChar) 
                      );
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for data sources that are SQL queries                 
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'SQL QUERIES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,coalesce(
                          datasourcetype || '(' || datasupplier || ' , ' || datasourcecomment|| ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || datasupplier || ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || to_char(createddate,'dd-mm-yyyy') || ')')
                      from datasourceob where datasourcetype = 'SQL' and  ( 
                         lower(physicalsourceuri) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasupplier) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcecomment) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcename) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcecontent) like lower(wildCardChar||searchText||wildCardChar) 
                      );
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;



          --*************************************************************************
          --* search for data sources that are form elements
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'FORM ELEMENTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid,coalesce(
                          datasourcetype || '(' || datasupplier || ' , ' || datasourcecomment|| ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || datasupplier || ' , ' || to_char(createddate,'dd-mm-yyyy') || ')',
                          datasourcetype || '(' || to_char(createddate,'dd-mm-yyyy') || ')')
                      from datasourceob where datasourcetype = 'Form Element' and  ( 
                         lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasupplier) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcecomment) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcename) like lower(wildCardChar||searchText||wildCardChar) or
                         lower(datasourcecontent) like lower(wildCardChar||searchText||wildCardChar) 
                      );
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for workflows                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'WORK FLOWS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from workflowob where ( lower(workflowdescription) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;
          --*************************************************************************
          --* search for workflowstages                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'WORK FLOW STAGES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from workflowstageob where ( lower(workflowstagedescription) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;
          --*************************************************************************
          --* search for microarray experiments                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'MICROARRAY EXPERIMENTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from geneexpressionstudy where
                   lower(studytype) like '%microarray%' and (
                   ( lower(xreflsid) like  lower(wildCardChar||searchText||wildCardChar))
                or ( lower(obkeywords) like lower(wildCardChar || searchText || wildCardChar))
                or ( lower(studydescription) like lower(wildCardChar || searchText || wildCardChar)));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search for genotype experiments                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'GENOTYPE EXPERIMENTS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from genotypestudy where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(studytype) like lower(wildCardChar||searchText||wildCardChar)) 
		      or ( lower(obkeywords) like lower(wildCardChar || searchText || wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

         --*************************************************************************
          --* search for phenotype studies                    
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'PHENOTYPE STUDIES' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from phenotypestudy where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
		      or ( lower(obkeywords) like lower(wildCardChar || searchText || wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


         --*************************************************************************
          --* search for genetic tests                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'GENETIC TESTS' then

             if position(wildCardChar in searchText) = 0  then
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| testdescription ,xreflsid)
                from genetictestfact where accession = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- no hit - try wildcard 
                open obCursor for select obid,xreflsid,
                coalesce(xreflsid  || ' '|| testdescription ,xreflsid) 
                from genetictestfact where lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar);
                fetch obCursor into listitem,listxreflsid;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
             else
                open obCursor for select obid,xreflsid from genetictestfact where lower(xreflsid) like lower(searchText);
                fetch obCursor into listitem,listxreflsid;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
             end if;
             close obCursor;

         --*************************************************************************
          --* search for genetic test runs                   
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'GENETIC TEST RUNS' then
             -- add items whose name matches the query
             open obCursor for select obid,xreflsid from genotypeobservation where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(genotypeobserved) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(genotypeobserveddescription) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(finalgenotype) like lower(wildCardChar||searchText||wildCardChar)) 
		      or ( lower(finalgenotypedescription) like lower(wildCardChar || searchText || wildCardChar))
		      or ( lower(observationcomment) like lower(wildCardChar || searchText || wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for biosubjects                  
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'BIOSUBJECTS' then
             -- add items whose name matches the query exactly
             tempCount := 0;
             open obCursor for select obid,xreflsid from biosubjectob where ( lower(xreflsid) = lower(searchText)) ;
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
                tempCount := tempCount + 1;
             end loop;
             close obCursor;

             -- if we got any exact matches , stop there, else search other fields
             if tempCount = 0 then
                open obCursor for select obid,xreflsid from biosubjectob where ( lower(xreflsid) like  lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(subjectspeciesname) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(subjectdescription) like lower(wildCardChar||searchText||wildCardChar));
                fetch obCursor into listitem,listxreflsid;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                   fetch obCursor into listitem,listxreflsid;
                   elementCount := elementCount + 1;
                end loop;
                close obCursor;
             end if;

          --*************************************************************************
          --* search for biosamples                 
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'BIOSAMPLES' then
             open obCursor for select obid,xreflsid from biosampleob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(samplename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(sampledescription) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(samplestorage) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for batches
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'BATCHES' then
             open obCursor for select obid,xreflsid from batchob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(batchname) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(batchdescription) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(batchtype) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;



          --*************************************************************************
          --* search for biolibraries
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'LIBRARIES' then
             open obCursor for select obid,xreflsid from biolibraryob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(libraryname) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(librarydescription) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(librarystorage) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for library sequencing
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'LIBRARY SEQUENCING' then
             open obCursor for select obid,xreflsid from librarysequencingfunction where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(runby) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(functioncomment) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for biosampling                 
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'BIOSAMPLING' then
             open obCursor for select obid,xreflsid from biosamplingfunction where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(samplingcomment) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for ontologies                
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'ONTOLOGIES' then
             open obCursor for select obid,xreflsid from ontologyob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(ontologydescription) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for ontology terms
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'ONTOLOGY TERMS' then
             -- if no wildcards try an exact match on the term
             if position(wildCardChar in searchText) = 0  then
                open obCursor for select obid , xreflsid , 
                coalesce(termname || ' '|| termdescription ,termname)
                from ontologytermfact where termname = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   fetch obCursor into listitem,listxreflsid, listcomment;
                   elementCount := elementCount + 1;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;
             end if;
             

             -- now try wildcard search (i.e. either they used wildcards or no hits yet)
             open obCursor for select obid,xreflsid,
                    coalesce(termname || ' '|| termdescription ,termname)
                    from ontologytermfact where lower(termname) like lower(wildCardChar||searchText||wildCardChar);

             fetch obCursor into listitem,listxreflsid,listcomment;

             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;

             close obCursor;
             if elementCount > 0 then
                update oblist set currentmembership = elementCount where obid = listid;
                return listid;
             end if;

             -- still no hit - try description and unitname
             open obCursor for select obid,xreflsid,
                    coalesce(termname || ' '|| termdescription ,termname)
                    from ontologytermfact where ( lower(termdescription) like lower(wildCardChar||searchText||wildCardChar))
                   or ( lower(unitname) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;

             close obCursor;

          --*************************************************************************
          --* search for databases
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATABASES' then
             open obCursor for select obid,xreflsid from biodatabaseob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(databasename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(databasedescription) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for database search runs
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'DATABASE SEARCHES' then
             open obCursor for select obid, xreflsid, coalesce(xreflsid  || ' : '|| studydescription ,xreflsid)  from databasesearchstudy 
             where lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar) ;
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for lab resources
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'ALL LAB RESOURCES' then
             open obCursor for select obid,xreflsid from labresourceob where ( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(resourcename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(resourcedescription) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(resourcetype) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(supplier) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for microarrays
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'MICROARRAYS' then
             open obCursor for select obid,xreflsid from labresourceob where resourcetype = 'microarray' and (( lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(resourcename) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(resourcedescription) like lower(wildCardChar||searchText||wildCardChar))
                      or ( lower(supplier) like lower(wildCardChar||searchText||wildCardChar)));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for comments
          --*
          --*************************************************************************
          elsif upper(obTypeName) = 'COMMENTS' then
             open obCursor for select obid,xreflsid from commentob where ( lower(createdby) like lower(searchText)) 
                      or ( lower(commentstring) like lower(wildCardChar||searchText||wildCardChar)) ;
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

          --*************************************************************************
          --* search for uri
          --*
          --*************************************************************************
          elsif upper(obTypeName) = 'EXTERNAL LINKS' then
             open obCursor for select obid,xreflsid from uriob where ( lower(createdby) like lower(searchText)) 
                      or ( lower(uristring) like lower(wildCardChar||searchText||wildCardChar)) 
                      or ( lower(uricomment) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


          --*************************************************************************
          --* search for biosequences              
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'BIOSEQUENCES' then



             -- if the search string does not contain a wildcard then first try to find an exact match on name 
             -- -  if we succeed then go no further
             -- first , name in sequence table....
             if position(wildCardChar in searchText) = 0  then
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                from biosequenceob where sequencename = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

               -- try lsid
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                from biosequenceob where xreflsid = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;


               -- try sequencename with .ab1 suffix
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                from biosequenceob where sequencename = searchText||'.ab1';
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;


                -- try splitting the sequecename name using an underscore character and using the second
                -- token as the sequence name (this is an adhoc rule used in some sequence databases , where there
                -- is a species or breed prefix. It probably should be shifted to a site-specific 
                -- search engine function
                if split_part(searchText,'_',2) is not null then
                   open obCursor for select obid , xreflsid, 
                   coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                   from biosequenceob where sequencename = split_part(searchText,'_',2);
                   fetch obCursor into listitem, listxreflsid, listcomment;
                   if FOUND then
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   end if;
                   close obCursor;

                   if elementCount > 0 then
                      update oblist set currentmembership = elementCount where obid = listid;
                      return listid;
                   end if;
                end if;

                -- if the search string is <= 5 characters this looks like a list name - try searching 
                -- for a sequence list 



             end if; -- no wildcards used - try exact match on names and return immediately if found


       


             --- from here , attempt wildcard matches on description and other fields -------




             -- add seqs that had blast hits to matching descriptions. 
             open obCursor for select obid,xreflsid , 
                ' ( hit to : ' || coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid) || ')'
                      from biosequenceob where ( lower(sequencedescription) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid, listcomment;
             while elementCount < maxListSize and FOUND LOOP
                open obCursor2 for select  
                querysequence from databasesearchobservation where hitsequence = listitem;
                fetch obCursor2 into listitem2;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor3 for select obid , xreflsid, 
                   coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                   from biosequenceob where obid = listitem2 and not exists
                   (select ob from listmembershiplink where oblist = listid and
                   ob = listitem2);
                   fetch obCursor3 into listitem3,listxreflsid3, listcomment3;
                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem3,listxreflsid3,listcomment);
                      fetch obCursor3 into listitem3,listxreflsid3, listcomment3;
                      elementCount := elementCount + 1;
                   end loop;
                   close obCursor3;
                   fetch obCursor2 into listitem2;
                end loop;
                close obCursor2;
                fetch obCursor into listitem,listxreflsid,listcomment;
             end loop;
             close obCursor;


             -- next add the seqs that had matching descriptions
	     if elementCount < maxListSize then
                open obCursor for select obid,xreflsid , 
                   coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid) 
                         from biosequenceob where ( lower(sequencedescription) like lower(wildCardChar||searchText||wildCardChar)) and
                         not exists 
                         (select ob from listmembershiplink where oblist = listid and
                         ob = biosequenceob.obid);             
                fetch obCursor into listitem,listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   fetch obCursor into listitem,listxreflsid,listcomment;
                   elementCount := elementCount + 1;
                end loop;
                close obCursor;
             end if;


             -- try wildcard on lsid
             open obCursor for select obid , xreflsid, 
             coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
             from biosequenceob where lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar);
             fetch obCursor into listitem, listxreflsid, listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                elementCount := elementCount + 1;
                fetch obCursor into listitem,listxreflsid, listcomment;
             end loop;
             close obCursor;


	     -- next add items from the seqfeaturefact table
             if sensitivity >= 3 then
	        if elementCount < maxListSize then
                   open obCursor for select distinct biosequenceob ,xreflsid  from biosequencefeaturefact f where 
                   f.featuretype = lower(searchText);
                   fetch obCursor into listitem,listxreflsid;
                   while elementCount < maxListSize and FOUND LOOP
                      open obCursor2 for select  
                      coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid) from biosequenceob where obid = listitem;
                      fetch obCursor2 into listcomment;
                      close obCursor2;
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      fetch obCursor into listitem,listxreflsid,listcomment;
                      elementCount := elementCount + 1;
                   end loop;
                   close obCursor;
                end if;
             end if;


             -- search gene ontology links
             --if elementCount < 30 then
             --   open obCursor for select ontologyob from ontologytermfact where lower(termname) like
             --   lower(wildCardChar||searchText||wildCardChar) and xreflsid like 'ontology.GO%';
             --   fetch obCursor into obvar1;
             --   while elementCount < maxListSize and FOUND LOOP
             --      open obCursor2 for select g.obid, replace(g.xreflsid,'geneticob.',''),
             --            coalesce(g.geneticobsymbols || ' '|| g.geneticobdescription ,
             --            g.geneticobsymbols,
             --            replace(g.xreflsid,'geneticob.','') || ' (symbol unknown)')
             --      from predicatelink pl join geneticob g on 
             --      pl.subjectob = g.obid and pl.objectob = obvar1;
             --      fetch obCursor2 into listitem,listxreflsid, listcomment;
             --      close obCursor2;
             --      if listitem is not null then
	     --         insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
             --         elementCount := elementCount + 1;
             --      end if;
             --      fetch obCursor into obvar1;
             --   end loop;
             --   close obCursor;
             --end if;



	     -- add sequences that are the gene products of genes that match the query - would
             -- be nice to do this recursively by a call to this method but this doesnt work
             -- (of course). The following code basically takes the above code for locating genes, 
             -- and joins to the geneproduct table

             -- **************** this was OK in SG which had a gene index but probably just slows down other 
             -- **************** instances. Perhaps we need to pass specific sensitivity and specificity hints to 
             -- **************** this method so we can control this. In the meantime I have stuck an internal 
             -- **************** sensitivity variable at the top
           
             if sensitivity >= 2 then

                -- first add items whose gene name matches the query
   	        if elementCount < maxListSize then
                   open obCursor for select gpl.biosequenceob , gpl.xreflsid from geneproductlink gpl, geneticob go where 
                   (lower(go.geneticobname) like lower(wildCardChar||searchText||wildCardChar)
                   or lower(go.geneticObSymbols) like lower(wildCardChar||searchText||wildCardChar)) and
                   gpl.geneticob = go.obid ; 
                   fetch obCursor into listitem,listxreflsid;
                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                      fetch obCursor into listitem,listxreflsid;
                      elementCount := elementCount + 1;
                   end loop;
                   close obCursor;
                end if;


                -- next add items whose description matches the query
                if elementCount < maxListSize then
                   open obCursor for select gpl.biosequenceob , gpl.xreflsid from geneproductlink gpl, geneticob go where 
                   (lower(go.geneticobdescription) like lower(wildCardChar||searchText||wildCardChar) or
                              lower(go.obkeywords) like lower(wildCardChar||searchText||wildCardChar)) and
                    gpl.geneticob = go.obid ;  
                   fetch obCursor into listitem,listxreflsid;
                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                      fetch obCursor into listitem,listxreflsid;
                      elementCount := elementCount + 1;
                   end loop;
                   close obCursor;
                end if; -- list not yet full


                -- add items whose function description matches the query
                if elementCount < maxListSize then
                   open obCursor for select distinct gpl.biosequenceob , gpl.xreflsid from geneproductlink gpl, geneticfunctionfact gff 
                   where lower(gff.functioncomment) like  lower(wildCardChar||searchText||wildCardChar) and
                   gpl.geneticob = gff.geneticob ;
                   fetch obCursor into listitem,listxreflsid;
                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                      fetch obCursor into listitem,listxreflsid;
                      elementCount := elementCount + 1;
                   end loop;
                   close obCursor;
                end if; -- list not yet full
             end if; -- sensitivity >= 2




          --*************************************************************************
          --* search for microarray spots                    
          --*
          --*************************************************************************

          elsif upper(obTypeName) = 'MICROARRAY SPOTS' then

             -- the strategy is currently as follows
             -- Exact matches (1) : 
             -- 1. Accession 
             -- 3. Gal_id
             -- 4. gal_name
             -- 5. xreflsid

             -- exact matches (2) :
             -- GO ontology on termname then link via GO association and sequence association


             -- exact matches (3) :
             -- biosequence on sequencename then link via sequence-spot link


             -- exact matches (4) , retrieve all records
             -- biosequence  on sequencename then link via blast hit

             -- wild cards or not hit yet :

       
             -- xreflsid
             -- accession
             -- spot description
             -- GO term description then link via GO association and sequence association
             -- sequence description then link via blast hits 



             -- if the search string does not contain a wildcard then first try to find an exact match on accession and 
             -- xreflsid before going any further
             if position(wildCardChar in searchText) = 0  then
                -- accession
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                from microarrayspotfact where accession = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- gal_id
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                from microarrayspotfact where gal_id = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- gal_name
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                from microarrayspotfact where gal_name = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- xreflsid
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                from microarrayspotfact where xreflsid = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND LOOP
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                   fetch obCursor into listitem, listxreflsid, listcomment;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;


                -- exact match on a sequencename (e.g. NCBI) , then via database hit and sequence association
                open obCursor for select obid, sequencedescription 
                from biosequenceob where sequencename = searchText;
                fetch obCursor into obvar1, textvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select msf.obid, msf.xreflsid, coalesce(msf.accession || ' ' || msf.gal_description || ' ' || textvar1,
                         msf.accession || ' ' || textvar1)  
                      from (databasesearchobservation dso join predicatelink plsa on 
                      dso.hitsequence = obvar1 and 
                      plsa.objectob = dso.querysequence and plsa.predicate = 'ARRAYSPOT-SEQUENCE') join
                      microarrayspotfact msf on msf.obid = plsa.subjectob ;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;

                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                      fetch obCursor2 into listitem, listxreflsid, listcomment;
                   end loop;
                   close obCursor2;

                   fetch obCursor into obvar1, textvar1;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;                





                -- exact match on go term via go association and sequence association
                open obCursor for select obid 
                from ontologytermfact where termname = searchText;
                fetch obCursor into obvar1;
                if elementCount < maxListSize and FOUND then
                   open obCursor2 for select msf.obid, msf.xreflsid, coalesce(msf.accession || ' ' || msf.gal_description,
                         msf.accession)  
                      from (predicatelink plgo join predicatelink plsa on 
                      plgo.objectob = obvar1 and plgo.predicate = 'GO_ASSOCIATION' and 
                      plsa.objectob = plgo.subjectob and plsa.predicate = 'ARRAYSPOT-SEQUENCE') join
                      microarrayspotfact msf on msf.obid = plsa.subjectob ;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;

                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                      fetch obCursor2 into listitem, listxreflsid, listcomment;
                   end loop;
                   close obCursor2;
                end if;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;
             end if;

             ---------------------------------------------------------
             ---- either no exact matches or wildcards were specified
             ---------------------------------------------------------


             -- first try items whose xreflsid can match the query
             open obCursor for select obid,xreflsid,coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                  from microarrayspotfact where lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar); 
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;

             -- if some hits on xreflsid were found, they are not searching using
             -- keywords, we can exit
             if elementCount > 0 then
                update oblist set currentmembership = elementCount where obid = listid;
                return listid;
             end if;


             -- next try items whose accession can match the query
             open obCursor for select obid,xreflsid,coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                  from microarrayspotfact where lower(accession) like lower(wildCardChar||searchText||wildCardChar); 
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


             -- next try items whose description can match the query
             open obCursor for select obid,xreflsid,coalesce(xreflsid  || ' '|| gal_description ,xreflsid)
                  from microarrayspotfact where lower(gal_description) like lower(wildCardChar||searchText||wildCardChar); 
             fetch obCursor into listitem,listxreflsid,listcomment;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid,membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                fetch obCursor into listitem,listxreflsid,listcomment;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;


             -- match go term via description and link via go association and sequence association
             if elementCount < maxListSize then
                open obCursor for select obid , termname || ' ' || termdescription
                from ontologytermfact where lower(termdescription) like lower(wildCardChar||searchText||wildCardChar);
                fetch obCursor into obvar1,textvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select msf.obid, msf.xreflsid, coalesce(msf.accession || ' ' || msf.gal_description || ' ' || textvar1,
                         msf.accession || ' ' || textvar1)  
                      from (predicatelink plgo join predicatelink plsa on 
                      plgo.objectob = obvar1 and plgo.predicate = 'GO_ASSOCIATION' and 
                      plsa.objectob = plgo.subjectob and plsa.predicate = 'ARRAYSPOT-SEQUENCE') join
                      microarrayspotfact msf on msf.obid = plsa.subjectob ;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;

                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                      fetch obCursor2 into listitem, listxreflsid, listcomment;
                   end loop;
                   close obCursor2;

                   fetch obCursor into obvar1,textvar1;
                end loop;
                close obCursor;

                -- if we got some hits using GO that will do
                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;
             end if;



             -- match sequence description , then via database hit and sequence association
             if elementCount < maxListSize then
                open obCursor for select obid, sequencedescription 
                from biosequenceob where lower(sequencedescription) like lower(wildCardChar||searchText||wildCardChar);
                fetch obCursor into obvar1, textvar1;
                while elementCount < maxListSize and FOUND LOOP
                   open obCursor2 for select msf.obid, msf.xreflsid, coalesce(msf.accession || ' ' || msf.gal_description || ' ' || textvar1,
                         msf.accession || ' ' || textvar1)  
                      from (databasesearchobservation dso join predicatelink plsa on 
                      dso.hitsequence = obvar1 and 
                      plsa.objectob = dso.querysequence and plsa.predicate = 'ARRAYSPOT-SEQUENCE') join
                      microarrayspotfact msf on msf.obid = plsa.subjectob ;
                   fetch obCursor2 into listitem,listxreflsid, listcomment;

                   while elementCount < maxListSize and FOUND LOOP
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                      fetch obCursor2 into listitem, listxreflsid, listcomment;
                   end loop;
                   close obCursor2;

                   fetch obCursor into obvar1, textvar1;
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;                
             end if;


          --*************************************************************************
          --* else do a basic search                   
          --*
          --*************************************************************************

          else 
             open obCursor for select obid,xreflsid from ob where obkeywords like lower(wildCardChar||searchText||wildCardChar);
             fetch obCursor into listitem,listxreflsid;
             while elementCount < maxListSize and FOUND LOOP
                insert into listmembershiplink(oblist,ob, obxreflsid) values (listid,listitem,listxreflsid);
                fetch obCursor into listitem,listxreflsid;
                elementCount := elementCount + 1;
             end loop;
             close obCursor;
          end if;


          -- finally , update the membership count of the list
          update oblist set currentmembership = currentmembership + elementCount where obid = listid;
       end if; -- no existing list could be re-used

       return listid;

    END;
$_$;


ALTER FUNCTION public.getsearchresultlisttest(text, character varying, integer, character varying, integer, integer, character varying) OWNER TO agrbrdf;

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

--
-- Name: getsitesearchresultlist(text, character varying, integer, character varying, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getsitesearchresultlist(text, character varying, integer, character varying, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   BEGIN
      return getSiteSearchResultList($1, $2, $3, $4, $5,0,null);
   END;
$_$;


ALTER FUNCTION public.getsitesearchresultlist(text, character varying, integer, character varying, integer) OWNER TO agrbrdf;

--
-- Name: getsitesearchresultlist(text, character varying, integer, character varying, integer, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getsitesearchresultlist(text, character varying, integer, character varying, integer, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   BEGIN
      return getSiteSearchResultList($1, $2, $3, $4, $5, $6,null);
   END;
$_$;


ALTER FUNCTION public.getsitesearchresultlist(text, character varying, integer, character varying, integer, integer) OWNER TO agrbrdf;

--
-- Name: getsitesearchresultlist(text, character varying, integer, character varying, integer, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getsitesearchresultlist(text, character varying, integer, character varying, integer, integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
    DECLARE
       obCursor refcursor;
       obCursor2 refcursor;


       searchTextArg ALIAS FOR $1;
       userName ALIAS FOR $2;
       maxListSize ALIAS FOR $3;
       obTypeName ALIAS FOR $4;
       useOldLimit ALIAS FOR $5;
       argListID ALIAS FOR $6;
       argListName ALIAS FOR $7;

       elementCount integer;
       tempCount integer;
       listid integer;
       listitem integer;
       listitem2 integer;
       obvar1 integer;
       textvar1 varchar;
       listxreflsid varchar;
       listxreflsid2 varchar;
       listcomment varchar;
       listcomment2 varchar;
       signature text;
       wildCardChar varchar;
       dollarChar varchar;
       searchText varchar;
       existingListID varchar;
       sensitivity integer;
    BEGIN
       -- ********** hard-coded PARAMETERS ************ ---
       sensitivity := 1;  -- use 2 or 3 for SG **** set this via arg list at some point ****
       elementCount := 0;
       wildCardChar := '%';
       /* dollarChar := '$'; */

       searchText := searchTextArg;

       -- if the user has provided a wildcard , do not insert one ourselves - also , support * wildcard
       if position('*' in searchText) > 0 then
          searchText := translate(searchText,'*',wildCardChar);
       end if;
       if position(wildCardChar in searchText) > 0  then
          wildCardChar := '';
       end if;

       existingListID := argListID;
       if existingListID is null then
          existingListID  := 0;
       end if;



       -- check if there is an existing list with the same signature, if useOldLimit >= 0, and if we have not been given an existing list to update
       /* signature := searchText || dollarChar || maxListSize || dollarChar || obTypeName; */
       signature = 'Search of ' || obTypeName || ' for ' || searchText || ' (limited to first ' || maxListSize || ' hits)';

       if upper(obTypeName) != 'PAST SEARCHES' and upper(obTypeName) != 'COMMENTS' and upper(obTypeName) != 'EXTERNAL LINKS' 
                      and upper(obTypeName) != 'DATA FILES SUBMITTED' and useOldLimit >= 0 and existingListID = 0 then
          select obid into listid from oblist where listdefinition = signature and statuscode > 0;
       end if;

       if (not FOUND ) or  not (upper(obTypeName) != 'PAST SEARCHES' and upper(obTypeName) != 'COMMENTS' and upper(obTypeName) != 'EXTERNAL LINKS' 
                      and upper(obTypeName) != 'DATA FILES SUBMITTED' and useOldLimit >= 0 and existingListID = 0 ) then
          if existingListID = 0 then
              -- create the list 
             open obCursor for select nextval('ob_obidseq');
             fetch obCursor into listid;
             close obCursor; 

             if argListName is not null then 
                signature := argListName;
             end if;
             

             insert into obList(obid,listName,listType,listDefinition,xreflsid,maxMembership,createdBy,displayurl)
             /* values(listid,'Search hits : ' || obTypeName ,'SEARCH_RESULT', searchText || dollarChar || maxListSize || dollarChar || obTypeName,searchText || dollarChar || maxListSize || dollarChar || obTypeName, maxListSize, userName); */
             values(listid,'Search hits : ' || obTypeName ,'SEARCH_RESULT', signature,signature, maxListSize, userName,'search.gif');

          else
             listid = existingListID;
          end if;
       
    
          -- populate the list. For each type there is an ordering to ensure that 
          -- the most relevant objects occur first in the list. Each type may involve searches of 
          -- several different database fields



          --*************************************************************************
          --* search for AgResearch Cattle sequences              
          --*
          --*************************************************************************

          if upper(obTypeName) = 'AGRESEARCH CATTLE SEQUENCES' then

             -- if the search string does not contain a wildcard then first try to find an exact match on name 
             -- -  if we succeed then go no further
             -- first , name in sequence table....
             if position(wildCardChar in searchText) = 0  then
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                from biosequenceob where sequencename = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                while elementCount < maxListSize and FOUND  LOOP
                   if isLSID(upper(obTypeName),listxreflsid) then
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   else
                      -- test whether can obtain any sequences that have a query-hit relationship with this
                      -- sequence as a hit
                      open obCursor2 for 
                      select b.obid,b.xreflsid , coalesce(b.xreflsid || ' hits ' || listxreflsid  || ' '|| listcomment ,b.xreflsid || ' hits ' || listxreflsid) 
                         from biosequenceob b join databasesearchobservation dob on 
                         dob.hitsequence = listitem and
                         b.obid = dob.querysequence;
                      fetch obCursor2 into listitem2,listxreflsid2, listcomment2;
                      while elementCount < maxListSize and FOUND  LOOP
                         if isLSID(upper(obTypeName),listxreflsid2) then
                            insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem2,listxreflsid2,listcomment2);
                            elementCount := elementCount + 1;
                         end if;
                         fetch obCursor2 into listitem2,listxreflsid2, listcomment2;
                      end loop;
                      close obCursor2;
                   end if;
                   fetch obCursor into listitem,listxreflsid, listcomment;
      
                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

                -- try lsid
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                from biosequenceob where xreflsid = searchText;
                fetch obCursor into listitem, listxreflsid, listcomment;
                

                while elementCount < maxListSize and FOUND  LOOP
                   if isLSID(upper(obTypeName),listxreflsid) then
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   else
                      -- test whether can obtain any sequences that have a query-hit relationship with this
                      -- sequence as a hit
                      open obCursor2 for 
                      select b.obid,b.xreflsid , coalesce(b.xreflsid || ' hits ' || listxreflsid  || ' '|| listcomment ,b.xreflsid || ' hits ' || listxreflsid) 
                         from biosequenceob b join databasesearchobservation dob on 
                         dob.hitsequence = listitem and
                         b.obid = dob.querysequence;
                      fetch obCursor2 into listitem2,listxreflsid2, listcomment2;
                      while elementCount < maxListSize and FOUND  LOOP
                         if isLSID(upper(obTypeName),listxreflsid2) then
                            insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem2,listxreflsid2,listcomment2);
                            elementCount := elementCount + 1;
                         end if;
                         fetch obCursor2 into listitem2,listxreflsid2, listcomment2;
                      end loop;
                      close obCursor2;
                   end if;
                   fetch obCursor into listitem,listxreflsid, listcomment;

                end loop;
                close obCursor;

                if elementCount > 0 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;


                -- try wildcard on just lsid
                open obCursor for select obid , xreflsid, 
                coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid)
                from biosequenceob where lower(xreflsid) like lower(wildCardChar||searchText||wildCardChar);
                fetch obCursor into listitem, listxreflsid, listcomment;
                while FOUND and elementCount < maxListSize  LOOP
                   if isLSID(upper(obTypeName),listxreflsid) then
                      insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                      elementCount := elementCount + 1;
                   else
                      -- test whether can obtain any sequences that have a query-hit relationship with this
                      -- sequence as a hit
                      open obCursor2 for 
                      select b.obid,b.xreflsid , coalesce(b.xreflsid || ' hits ' || listxreflsid  || ' '|| listcomment ,b.xreflsid || ' hits ' || listxreflsid) 
                         from biosequenceob b join databasesearchobservation dob on 
                         dob.hitsequence = listitem and
                         b.obid = dob.querysequence;
                      fetch obCursor2 into listitem2,listxreflsid2, listcomment2;
                      while elementCount < maxListSize and FOUND  LOOP
                         if isLSID(upper(obTypeName),listxreflsid2) then
                            insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem2,listxreflsid2,listcomment2);
                            elementCount := elementCount + 1;
                         end if;
                         fetch obCursor2 into listitem2,listxreflsid2, listcomment2;
                      end loop;
                      close obCursor2;
                   end if;
                   fetch obCursor into listitem,listxreflsid, listcomment;
                end loop;
                close obCursor;

                --if they get one result then stop here - else the search is non-specific so keep going
                if elementCount = 1 then
                   update oblist set currentmembership = elementCount where obid = listid;
                   return listid;
                end if;

             end if; -- no wildcards used - try exact match on names and return immediately if found



             --- from here , attempt matches using wildcards and other fields 
             open obCursor for select obid,xreflsid , 
                coalesce(xreflsid  || ' '|| sequencedescription ,xreflsid) 
                      from biosequenceob where (  
                      lower(obkeywords) like lower(wildCardChar||searchText||wildCardChar) or
      lower(sequencedescription) like lower(wildCardChar||searchText||wildCardChar));
             fetch obCursor into listitem,listxreflsid, listcomment;
             while elementCount < maxListSize and FOUND  LOOP
                if isLSID(upper(obTypeName),listxreflsid) then
                   insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem,listxreflsid,listcomment);
                   elementCount := elementCount + 1;
                else
                   -- test whether can obtain any sequences that have a query-hit relationship with this
                   -- sequence as a hit
                   open obCursor2 for 
                   select b.obid,b.xreflsid , coalesce(b.xreflsid || ' hits ' || listxreflsid  || ' '|| listcomment ,b.xreflsid || ' hits ' || listxreflsid) 
                      from biosequenceob b join databasesearchobservation dob on 
                      dob.hitsequence = listitem and
                      b.obid = dob.querysequence;
                   fetch obCursor2 into listitem2,listxreflsid2, listcomment2;
                   while elementCount < maxListSize and FOUND  LOOP
                      if isLSID(upper(obTypeName),listxreflsid2) then
                         insert into listmembershiplink(oblist,ob, obxreflsid, membershipcomment) values (listid,listitem2,listxreflsid2,listcomment2);
                         elementCount := elementCount + 1;
                      end if;
                      fetch obCursor2 into listitem2,listxreflsid2, listcomment2;
                   end loop;
                   close obCursor2;
                end if;
                fetch obCursor into listitem,listxreflsid, listcomment;
             end loop;
             close obCursor;

             /*
             * the main search method includes searches of various related tables
             * which are not currently supported here as there is nothing in them
             */

          end if;


          -- finally , update the membership count of the list
          update oblist set currentmembership = currentmembership + elementCount where obid = listid;
       end if; -- no existing list could be re-used

       return listid;

    END;
$_$;


ALTER FUNCTION public.getsitesearchresultlist(text, character varying, integer, character varying, integer, integer, character varying) OWNER TO agrbrdf;

--
-- Name: getsubjectcharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getsubjectcharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        subjectobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from biosubjectfact 
      where biosubjectob = subjectobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getsubjectcharfact(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: gettopsearchhit(integer, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhit(integer, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
   BEGIN   
      return getTopSearchHit(seqobid, studyobid, null);
    END;
$_$;


ALTER FUNCTION public.gettopsearchhit(integer, integer) OWNER TO agrbrdf;

--
-- Name: gettopsearchhit(integer, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhit(integer, integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
      tophit int4;
      topobservation int4;
   BEGIN   
      select getTopSearchObservation(seqobid, studyobid, argflag) into topobservation;
      if topobservation  is null then
         return null;
      end if;

      select hitsequence into tophit from databasesearchobservation where obid = topobservation;

      return tophit;
    END;
$_$;


ALTER FUNCTION public.gettopsearchhit(integer, integer, character varying) OWNER TO agrbrdf;

--
-- Name: gettopsearchhit(character varying, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhit(character varying, integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqname ALIAS for $1;
      seqobid int4;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
      tophit int4;
      topobservation int4;
   BEGIN   
      seqobid := null;

      select obid into seqobid from biosequenceob where sequencename = seqname;

      if seqobid is null then
          return null;
      else
          return getTopSearchHit(seqobid,studyobid,argflag);
      end if;
    END;
$_$;


ALTER FUNCTION public.gettopsearchhit(character varying, integer, character varying) OWNER TO agrbrdf;

--
-- Name: gettopsearchhitattribute(integer, integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhitattribute(integer, integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
      attributename ALIAS for $4;
      tophitattribute varchar(5196);
      tophit integer;
      topobservation integer;
   BEGIN
      if upper(attributename) != 'HITFROM' and upper(attributename) != 'HITTO' and upper(attributename) != 'EVALUE'  and
         upper(attributename) != 'QUERYFROM' and upper(attributename) != 'QUERYTO'  and upper(attributename) != 'NEWFLAG' and
         upper(attributename) != 'QUERYFRAME'  and upper(attributename) != 'HITSTRAND' then
         tophit := getTopSearchHit(seqobid,studyobid,argflag);
         tophitattribute := null;
         if tophit is not null then
            if upper(attributename) = 'NAME' then
               open hitcursor for 
               select sequencename from 
               biosequenceob where obid = tophit;
            elsif  upper(attributename) = 'NAME AND DESCRIPTION' then
               open hitcursor for 
               select coalesce(sequencename || ' ' || sequencedescription, sequencename) from 
               biosequenceob where obid = tophit; 
            elsif  upper(attributename) = 'DESCRIPTION' then
               open hitcursor for 
               select sequencedescription from 
               biosequenceob where obid = tophit; 
            else 
               raise Exception 'unknown attribute specification';
            end if;
            fetch hitcursor into tophitattribute;
            close hitcursor;
         end if;
      else 
         topobservation := getTopSearchObservation(seqobid,studyobid,argflag);
         tophitattribute := null;
         if topobservation is not null then
            if upper(attributename) = 'QUERYTO' then
               open hitcursor for 
               select to_char(queryto,'9999999999') from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif  upper(attributename) = 'QUERYFROM' then
               open hitcursor for 
               select to_char(queryfrom,'9999999999')  from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif upper(attributename) = 'HITTO' then
               open hitcursor for 
               select to_char(hitto,'9999999999') from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif  upper(attributename) = 'HITFROM' then
               open hitcursor for 
               select to_char(hitfrom,'9999999999')  from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif  upper(attributename) = 'QUERYFRAME' then
               open hitcursor for 
               select to_char(queryframe,'9999999999')  from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif  upper(attributename) = 'HITSTRAND' then
               open hitcursor for 
               select to_char(hitstrand,'9999999999')  from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif  upper(attributename) = 'EVALUE' then
               open hitcursor for 
               select format_evalue(hitevalue)  from 
               databasesearchobservation  where obid = topobservation;
            elsif  upper(attributename) = 'NEWFLAG' then
               open hitcursor for 
               select 
                  case
                     when upper(userflags) like '%NEW%' then 'New' 
                     else null
                  end 
               from  
               databasesearchobservation  where obid = topobservation; 
            else 
               raise exception 'unsupported attribute % ', attributename;
            end if;
 
            fetch hitcursor into tophitattribute;

            close hitcursor;
         end if;
      end if;
     
      return tophitattribute;
   END;
$_$;


ALTER FUNCTION public.gettopsearchhitattribute(integer, integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: gettopsearchhitattribute(character varying, integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhitattribute(character varying, integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqobid int4;
      seqname ALIAS for $1;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
      attributename ALIAS for $4;
      tophitattribute varchar(5196);
      tophit integer;
      topobservation integer;
  BEGIN
      seqobid := null;

      select obid into seqobid from biosequenceob where sequencename = seqname;

      if seqobid is null then
          return null;
      else
          return getTopSearchHitAttribute(seqobid, studyobid,argflag,attributename);
      end if;
  END;
$_$;


ALTER FUNCTION public.gettopsearchhitattribute(character varying, integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: gettopsearchhitname(integer, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhitname(integer, integer, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
   BEGIN
      return getTopSearchHitAttribute(seqobid,studyobid,argflag,'NAME');
   END;
$_$;


ALTER FUNCTION public.gettopsearchhitname(integer, integer, character varying) OWNER TO agrbrdf;

--
-- Name: gettopsearchobservation(integer, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchobservation(integer, integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
      topobservation int4;
   BEGIN   
      if seqobid is null then
         return null;
      end if;

      if argflag is null then 
         open hitcursor for
           select
              dso.obid
            from 
               databasesearchobservation dso left outer join sequencealignmentfact saf on
               saf.databasesearchobservation = dso.obid
            where           
               dso.databasesearchstudy = studyobid and 
               dso.querysequence = seqobid 
            order by
               dso.hitevalue asc,
               saf.bitscore desc;
      else
         open hitcursor for 
           select
              dso.obid
            from 
               databasesearchobservation dso left outer join sequencealignmentfact saf on
               saf.databasesearchobservation = dso.obid
            where           
               dso.databasesearchstudy = studyobid and 
               dso.querysequence = seqobid and
               dso.userflags like '%'||argflag||'%'
            order by
               dso.hitevalue asc,
               saf.bitscore desc;
      end if;


      fetch hitcursor into topobservation;
      if not FOUND then
         topobservation := null;
      end if;
      close hitcursor;
      return topobservation;
    END;
$_$;


ALTER FUNCTION public.gettopsearchobservation(integer, integer, character varying) OWNER TO agrbrdf;

--
-- Name: gettopsearchquery(integer, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchquery(integer, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
      tophit int4;
   BEGIN   

      if seqobid is null then
         return null;
      end if;


      open hitcursor for
    select
          querysequence
        from 
           databasesearchobservation dso left outer join sequencealignmentfact saf on
           saf.databasesearchobservation = dso.obid
        where
           dso.databasesearchstudy = studyobid and 
           dso.hitsequence = seqobid
        order by
           dso.hitevalue asc,
           saf.bitscore desc;
      fetch hitcursor into tophit;
      if not FOUND then
         tophit := null;
      end if;
      close hitcursor;
      return tophit;
    END;
$_$;


ALTER FUNCTION public.gettopsearchquery(integer, integer) OWNER TO agrbrdf;

--
-- Name: inlistwithterm(integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION inlistwithterm(integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$  

DECLARE
   mycur refcursor;
   myob alias for $1;
   myterm alias for $2;
   myresult integer;
BEGIN  
   myresult := 0;

   open mycur for 
      select 1 from oblist where upper(listdefinition) like '%' ||upper(myterm)||'%'
      and exists (select 1 from listmembershiplink where oblist = oblist.obid and ob = myob);

   fetch mycur into myresult;

   if not found then
      myresult := 0;
   else 
      myresult := 1;
   end if;
   
   close mycur;

   return myresult;
END
$_$;


ALTER FUNCTION public.inlistwithterm(integer, character varying) OWNER TO agrbrdf;

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

--
-- Name: islsid(text, text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION islsid(text, text) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      arglsidtype alias for $1;
      arglsid alias for $2;
   BEGIN
      if upper(arglsidtype) = 'AGRESEARCH CATTLE SEQUENCES' then
         if upper(arglsid) like 'CS34%' or 
            upper(arglsid) like 'CS20%' or 
            upper(arglsid) like 'CS14%' or 
            upper(arglsid) like 'AGRESEARCH.BOVINE%' 
            then
            return true;
         else
            return false;
         end if;
      else
         return true;
      end if;
   END;
$_$;


ALTER FUNCTION public.islsid(text, text) OWNER TO agrbrdf;

--
-- Name: lasttoken(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION lasttoken(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   instring alias for $1;
   separator alias for $2;
   sepcount int4;
   ltoken varchar;
   rtoken varchar;
   tokenresult varchar;
begin
   tokenresult := instring;

   -- get how may separators there are 
   sepcount = length(instring) - length(replace(instring,separator,''));

   if sepcount >= 1 then
      ltoken = rtrim(ltrim(split_part(instring,separator,sepcount)));
      rtoken = rtrim(ltrim(split_part(instring,separator,sepcount + 1)));

      tokenresult := rtoken;

      if length(rtoken) = 0 then
         tokenresult := ltoken;
      end if;
   end if;
   
   return tokenresult;
end;$_$;


ALTER FUNCTION public.lasttoken(character varying, character varying) OWNER TO agrbrdf;

--
-- Name: makefasta(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION makefasta(character varying, character varying) RETURNS text
    LANGUAGE plpgsql
    AS $_$  

DECLARE
   idline alias for $1;
   seqstring alias for $2;
   strbuff text;
   seqpos integer;

BEGIN   
   strbuff := '>' || idline || chr(10);

   seqpos := 1;

   while seqpos <= length(seqstring) loop
      strbuff := strbuff || substr(seqstring,seqpos,60) || chr(10);
      seqpos := seqpos + 60;
   end loop;

   return strbuff;
END
$_$;


ALTER FUNCTION public.makefasta(character varying, character varying) OWNER TO agrbrdf;

--
-- Name: makehyperlink(character varying, character varying, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION makehyperlink(character varying, character varying, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   argurl alias for $1;
   argdisplay alias for $2;
   argurlbindvalue alias for $3;
   argtarget alias for $4;
   hyperlink varchar(5192);
BEGIN
   hyperlink := argurl;
 
   if argurlbindvalue is not null then
      hyperlink := replace(hyperlink,'$$',argurlbindvalue);
   end if;

   hyperlink := '<a href="' || hyperlink || '" ';

   if argtarget is not null then 
      hyperlink := hyperlink || ' target=' || argtarget;
   end if;

   hyperlink := hyperlink || '>' || argdisplay || '</a>';

   return hyperlink;
END;
$_$;


ALTER FUNCTION public.makehyperlink(character varying, character varying, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: markfeature(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION markfeature(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql IMMUTABLE
    AS $_$
declare
   argobid alias for $1;
   argfeaturetype alias for $2;
   markmethod alias for $3;
   markedseqstring varchar;
   featstart integer;
   featstop integer;
   featstrand integer;
   featCursor refcursor;
begin

   if markmethod != 'lowercase' and markmethod != 'X' then
      raise exception 'only lower case or X masking is currently supported';
   end if;

  
   -- examples : 7612140, 7466140
   select seqstring into markedseqstring from 
   biosequenceob where obid = argobid;

   

   open featCursor for 
   select featurestart,featurestop,featurestrand
   from biosequencefeaturefact where
   biosequenceob = argobid and featuretype = argfeaturetype;

   fetch featCursor into featstart,featstop,featstrand;

   while FOUND loop
      if featstrand <= 0  then
         raise exception 'only features on + strand are currently supported';
      end if;
 
      markedseqstring := overlay(markedseqstring placing lower(substr(markedseqstring,featstart,1+featstop-featstart)) from featstart for 1+ featstop-featstart );    

      fetch featCursor into featstart,featstop,featstrand;
   end loop;

   close featCursor;

   if markmethod = 'X' then
      markedseqstring := replace(replace(replace(replace(markedseqstring,'a','X'),'c','X'),'g','X'),'t','X');
   end if;
  
   return markedseqstring;
end;
$_$;


ALTER FUNCTION public.markfeature(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: mylog(integer, text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION mylog(integer, text) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
declare
   argorder alias for $1;
   argtext alias for $2;
begin
   insert into mylogger(msgorder,msgtext) 
   values(argorder,argtext);
   return 0;
end;
$_$;


ALTER FUNCTION public.mylog(integer, text) OWNER TO agrbrdf;

--
-- Name: newline_concat(text, text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION newline_concat(text, text) RETURNS text
    LANGUAGE plpgsql
    AS $_$
   declare
      arg1 alias for $1;
      arg2 alias for $2;
   begin
      if length(arg1) > 0 then
         return arg1||'
'||arg2 ;
      else
         return arg1||arg2 ;
      end if;
   end;
$_$;


ALTER FUNCTION public.newline_concat(text, text) OWNER TO agrbrdf;

--
-- Name: setobtype(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION setobtype() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        NEW.obtypeid = TG_ARGV[0];
        NEW.createddate = now();
        RETURN NEW;
    END;
$$;


ALTER FUNCTION public.setobtype() OWNER TO agrbrdf;

--
-- Name: testarray(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION testarray() RETURNS integer
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms integer[];
    BEGIN
        terms[3]=4;
        return terms[3];
    END;
$$;


ALTER FUNCTION public.testarray() OWNER TO agrbrdf;

--
-- Name: testfn(integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION testfn(integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
   testvar integer[];
begin
   testvar[1] := 2;
   testvar[3] := 4;
end;
$$;


ALTER FUNCTION public.testfn(integer) OWNER TO agrbrdf;

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

--
-- Name: agg_comma_concat(text); Type: AGGREGATE; Schema: public; Owner: agrbrdf
--

CREATE AGGREGATE agg_comma_concat(text) (
    SFUNC = comma_concat,
    STYPE = text,
    INITCOND = ''
);


ALTER AGGREGATE public.agg_comma_concat(text) OWNER TO agrbrdf;

--
-- Name: agg_comment_concat(text); Type: AGGREGATE; Schema: public; Owner: agrbrdf
--

CREATE AGGREGATE agg_comment_concat(text) (
    SFUNC = comment_concat,
    STYPE = text,
    INITCOND = ''
);


ALTER AGGREGATE public.agg_comment_concat(text) OWNER TO agrbrdf;

--
-- Name: agg_newline_concat(text); Type: AGGREGATE; Schema: public; Owner: agrbrdf
--

CREATE AGGREGATE agg_newline_concat(text) (
    SFUNC = newline_concat,
    STYPE = text,
    INITCOND = ''
);


ALTER AGGREGATE public.agg_newline_concat(text) OWNER TO agrbrdf;

SET default_tablespace = '';

SET default_with_oids = true;

--
-- Name: SEQSOURCE; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE "SEQSOURCE" (
    "SOURCECODE" character varying(50),
    "ORGANISMNAME" character varying(100),
    "ANIMALNAME" character varying(100),
    "SEX" character varying(16),
    "ORGAN" character varying(100),
    "TISSUE" character varying(2000),
    "AGE" character varying(100),
    "PRIMERDNA" double precision,
    "PRIMERPCR" double precision,
    "DESCRIPTION" character varying(1000),
    "ALTLIBNUM" double precision,
    "ORGANISMCODE" character varying(64),
    "BREED" character varying(128),
    "STRATEGYDESCRIPTION" character varying(2000),
    "TAXONID" double precision,
    "GENOTYPE" character varying(100),
    "PHENOTYPE" character varying(100),
    "KINGDOM" character varying(64),
    "SECONDSPECIESTAXID" double precision,
    "STRAIN" character varying(64),
    "CULTIVAR" character varying(64),
    "VARIETY" character varying(64),
    "SEQUENCETYPE" character varying(64),
    "SEQUENCESUBTYPE" character varying(64),
    "EXPECTEDSIZE" double precision,
    "ACCESS_FLAG" double precision,
    "PROJECTID" double precision,
    "PREPARATION_PROTOCOL" character varying(4000),
    "FVECTOR_NAME" character varying(64),
    "FVECTOR_DBXREF" character varying(64),
    "RVECTOR_NAME" character varying(64),
    "RVECTOR_DBXREF" character varying(64),
    "LIBPREPDATE" timestamp(0) without time zone,
    "LIBPREPAREDBY" character varying(64),
    "DATASUBMITTEDBY" character varying(64),
    "GROWTH_CULTURE_AGE" double precision,
    "GROWTH_MEDIUM" character varying(64),
    "GROWTH_CONDITIONS" character varying(4000),
    "VECTOR_SUPPLIER" character varying(64),
    "RESTRICTION_ENZYMES" character varying(4000),
    "INSERTS_SIZE" character varying(64),
    "HOST_STRAIN" character varying(64),
    "AMPLIFIED" double precision,
    "LABBOOK_OWNER" character varying(64),
    "LABBOOK_REF" character varying(64),
    "LABBOOK_PAGES" character varying(64),
    "PROJECTCODEID" double precision,
    "SEQDBID" double precision
);


ALTER TABLE public."SEQSOURCE" OWNER TO agrbrdf;

--
-- Name: SEQSOURCE_DETAIL; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE "SEQSOURCE_DETAIL" (
    "SOURCECODE" character varying(50),
    "DETAIL_NAME" character varying(64),
    "DETAIL_VALUE" character varying(4000)
);


ALTER TABLE public."SEQSOURCE_DETAIL" OWNER TO agrbrdf;

SET default_with_oids = false;

--
-- Name: accessfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE accessfact (
    ob integer NOT NULL,
    accesstype character varying(64),
    accesscomment text,
    createddate date DEFAULT now(),
    createdby character varying(256),
    lastupdateddate date,
    lastupdatedby character varying(256)
);


ALTER TABLE public.accessfact OWNER TO agrbrdf;

--
-- Name: accesslink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE accesslink (
    ob integer NOT NULL,
    staffob integer,
    oblist integer,
    accesstype character varying(64),
    accesscomment text,
    createddate date DEFAULT now(),
    createdby character varying(256),
    lastupdateddate date,
    lastupdatedby character varying(256)
);


ALTER TABLE public.accesslink OWNER TO agrbrdf;

--
-- Name: ob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE ob (
    obid integer DEFAULT nextval(('ob_obidseq'::text)::regclass) NOT NULL,
    obtypeid integer DEFAULT 0 NOT NULL,
    xreflsid character varying(2048) NOT NULL,
    createddate date DEFAULT now(),
    createdby character varying(256),
    lastupdateddate date,
    lastupdatedby character varying(256),
    checkedout boolean DEFAULT false,
    checkedoutby character varying(256),
    checkoutdate date,
    obkeywords character varying(4096),
    statuscode integer DEFAULT 1
);


ALTER TABLE public.ob OWNER TO agrbrdf;

--
-- Name: TABLE ob; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON TABLE ob IS 'Most objects and relations are stored in tables that inherit from the ob table, and hence 
each instance is assigned a unique numeric name (obid)';


--
-- Name: COLUMN ob.obid; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN ob.obid IS 'obid is the principal internal unique identifier for each object. Note that obid is not portable - e.g. on 
import of the data to a new instance, obid may be different. obid is distinct from the postgres OID';


--
-- Name: COLUMN ob.xreflsid; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN ob.xreflsid IS 'This is a pseudo lsid (life sciences identifier), for each object - a human readable unique name. Note that
the xreflsid is not in fact guaranteed to be unique, and would need to be processed by an lsid filter before being published as a true lsid';


--
-- Name: op; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE op (
    voptypeid integer
)
INHERITS (ob);


ALTER TABLE public.op OWNER TO agrbrdf;

--
-- Name: analysisfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE analysisfunction (
    ob integer NOT NULL,
    datasourcelist integer,
    datasourcedescriptors text,
    analysisprocedureob integer NOT NULL,
    functioncomment character varying(1024),
    invocation text,
    invocationorder integer,
    datasourceob integer,
    CONSTRAINT analysisfunction_obtypeid_check CHECK ((obtypeid = 545))
)
INHERITS (op);


ALTER TABLE public.analysisfunction OWNER TO agrbrdf;

--
-- Name: analysisprocedurefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE analysisprocedurefact (
    analysisprocedureob integer NOT NULL,
    factnamespace character varying(256),
    attributedate date,
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.analysisprocedurefact OWNER TO agrbrdf;

--
-- Name: analysisprocedureob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE analysisprocedureob (
    procedurename character varying(1024),
    author character varying(2048),
    authordate date,
    sourcecode text,
    proceduredescription character varying(1024),
    procedurecomment text,
    proceduretype character varying(64),
    invocation text,
    presentationtemplate text,
    textincount integer,
    textoutcount integer,
    imageoutcount integer,
    CONSTRAINT analysisprocedureob_obtypeid_check CHECK ((obtypeid = 540))
)
INHERITS (ob);


ALTER TABLE public.analysisprocedureob OWNER TO agrbrdf;

--
-- Name: anneoconnelarrays2; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE anneoconnelarrays2 (
    col integer,
    added character varying(10),
    differential character varying(30),
    probes character varying(30),
    probes_1 character varying(10),
    col_1 character varying(20),
    gene_id character varying(20),
    pubmatrix_submitted character varying(10),
    category character varying(140),
    gene_symbol character varying(20),
    est_length character varying(10),
    mean_intensity character varying(20),
    est1_w172_high double precision,
    est2_w230_high double precision,
    est3_w1215_high double precision,
    est4_w1276_high double precision,
    est5_w269_high double precision,
    est9_w156_neutral double precision,
    est6_w173_neutral double precision,
    est7_w209_low double precision,
    est10_w296_low double precision,
    est8_w1322_low double precision,
    df integer,
    n1 double precision,
    maximum double precision,
    stdev character varying(10),
    low character varying(10),
    high character varying(10),
    high_low character varying(10),
    res_sd double precision,
    dbias double precision,
    se1_w172 double precision,
    se2_w230 double precision,
    se3_w1215 double precision,
    se4_w1276 double precision,
    se5_w269 double precision,
    se6_w173 double precision,
    se7_w209 double precision,
    se8_w1322 double precision,
    se9_w156 double precision,
    se10_w296 double precision,
    cont1_low_vs_high double precision,
    fold_differnce_lowoverhigh_pct_mean double precision,
    high_versus_low double precision,
    secont1_low_vs_high double precision,
    tcont1_low_vs_high double precision,
    prcont1_low_vs_high double precision,
    modt_low_vs_high double precision,
    mod_sd_low_vs_high double precision,
    mod_pr_low_vs_high double precision,
    minuslogp_low_vs_high double precision,
    probes_2 character varying(20),
    datasourceob integer,
    voptypeid integer,
    dbprobes character varying(30)
);


ALTER TABLE public.anneoconnelarrays2 OWNER TO agrbrdf;

--
-- Name: anneoconnelprobenames; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE anneoconnelprobenames (
    col integer,
    col_1 character varying(10),
    propname character varying(20),
    col_2 character varying(10),
    genename character varying(20),
    col_3 character varying(20),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.anneoconnelprobenames OWNER TO agrbrdf;

--
-- Name: anneoconnelprobenames_bak; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE anneoconnelprobenames_bak (
    col integer,
    col_1 character varying(10),
    propname character varying(20),
    col_2 character varying(10),
    genename character varying(20),
    col_3 character varying(20),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.anneoconnelprobenames_bak OWNER TO agrbrdf;

--
-- Name: arrayexpressorthologs; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE arrayexpressorthologs (
    arrayexpressseq character varying(2048),
    zebraortholog integer,
    platypusortholog integer
);


ALTER TABLE public.arrayexpressorthologs OWNER TO agrbrdf;

--
-- Name: biodatabasefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biodatabasefact (
    biodatabaseob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.biodatabasefact OWNER TO agrbrdf;

--
-- Name: biodatabaseob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biodatabaseob (
    databasename character varying(256),
    databasedescription character varying(2048),
    databasetype character varying(2048),
    databasecomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 315))
)
INHERITS (ob);


ALTER TABLE public.biodatabaseob OWNER TO agrbrdf;

--
-- Name: biolibraryconstructionfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biolibraryconstructionfunction (
    biosampleob integer NOT NULL,
    biolibraryob integer NOT NULL,
    bioprotocolob integer,
    labresourcelist integer,
    labresourceob integer,
    labbookreference character varying(2048),
    constructioncomment character varying(1024),
    constructiondate date,
    CONSTRAINT biolibraryconstructionfunction_obtypeid_check CHECK ((obtypeid = 495))
)
INHERITS (op);


ALTER TABLE public.biolibraryconstructionfunction OWNER TO agrbrdf;

--
-- Name: biolibraryfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biolibraryfact (
    biolibraryob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.biolibraryfact OWNER TO agrbrdf;

--
-- Name: biolibraryob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biolibraryob (
    libraryname character varying(1024),
    librarytype character varying(256),
    librarydate date,
    librarydescription text,
    librarystorage text,
    CONSTRAINT biolibraryob_obtypeid_check CHECK ((obtypeid = 485))
)
INHERITS (ob);


ALTER TABLE public.biolibraryob OWNER TO agrbrdf;

--
-- Name: bioprotocolob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE bioprotocolob (
    protocolname character varying(1024),
    protocoltype character varying(1024),
    protocoldescription character varying(1024),
    protocoltext text,
    CONSTRAINT "$1" CHECK ((obtypeid = 95))
)
INHERITS (ob);


ALTER TABLE public.bioprotocolob OWNER TO agrbrdf;

--
-- Name: biosamplealiquotfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplealiquotfact (
    biosampleob integer NOT NULL,
    aliquotvolume double precision,
    aliquotvolumeunit character varying(64),
    aliquotcount double precision,
    aliquotcountunit character varying(64),
    aliquotweight double precision,
    aliquotweightunit character varying(64),
    aliquotdme double precision,
    aliquotdmeunit character varying(64),
    aliquottype character varying(64),
    aliquotdate date,
    aliquotcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 400))
)
INHERITS (op);


ALTER TABLE public.biosamplealiquotfact OWNER TO agrbrdf;

--
-- Name: biosamplealiquotfact2; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplealiquotfact2 (
    biosamplealiquotfact integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.biosamplealiquotfact2 OWNER TO agrbrdf;

--
-- Name: biosamplefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplefact (
    biosampleob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.biosamplefact OWNER TO agrbrdf;

--
-- Name: biosamplelist; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplelist (
    listname character varying(256) NOT NULL,
    maxmembership integer,
    listcomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 102))
)
INHERITS (ob);


ALTER TABLE public.biosamplelist OWNER TO agrbrdf;

--
-- Name: biosamplelistmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplelistmembershiplink (
    biosamplelist integer NOT NULL,
    biosampleob integer NOT NULL,
    inclusioncomment character varying(64),
    addeddate date DEFAULT now(),
    addedby character varying(256)
);


ALTER TABLE public.biosamplelistmembershiplink OWNER TO agrbrdf;

--
-- Name: biosampleob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosampleob (
    samplename character varying(1024),
    sampletype character varying(256),
    sampletissue character varying(256),
    sampledate date,
    sampledescription text,
    samplestorage text,
    samplecount double precision,
    samplecountunit character varying(64),
    sampleweight double precision,
    sampleweightunit character varying(64),
    samplevolume double precision,
    samplevolumeunit character varying(64),
    sampledrymatterequiv double precision,
    sampledmeunit character varying(64),
    CONSTRAINT "$1" CHECK ((obtypeid = 90))
)
INHERITS (ob);


ALTER TABLE public.biosampleob OWNER TO agrbrdf;

--
-- Name: biosamplingfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplingfact (
    biosamplingfunction integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096),
    unitname character varying(256)
);


ALTER TABLE public.biosamplingfact OWNER TO agrbrdf;

--
-- Name: biosamplingfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplingfunction (
    biosubjectob integer NOT NULL,
    biosampleob integer NOT NULL,
    bioprotocolob integer,
    labresourcelist integer,
    labresourceob integer,
    labbookreference character varying(2048),
    samplingcomment character varying(1024),
    samplingdate date,
    CONSTRAINT "$1" CHECK ((obtypeid = 100))
)
INHERITS (op);


ALTER TABLE public.biosamplingfunction OWNER TO agrbrdf;

--
-- Name: biosequencefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosequencefact (
    biosequenceob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.biosequencefact OWNER TO agrbrdf;

--
-- Name: biosequencefeatureattributefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosequencefeatureattributefact (
    biosequencefeaturefact integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.biosequencefeatureattributefact OWNER TO agrbrdf;

--
-- Name: biosequencefeaturefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosequencefeaturefact (
    biosequenceob integer NOT NULL,
    featuretype character varying(256),
    featureaccession character varying(256),
    featurestart integer,
    featurestop integer,
    featurestrand integer,
    featurecomment text,
    evidence text,
    featurelength integer,
    score double precision,
    CONSTRAINT "$1" CHECK ((obtypeid = 117))
)
INHERITS (op);


ALTER TABLE public.biosequencefeaturefact OWNER TO agrbrdf;

--
-- Name: biosequenceob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosequenceob (
    sequencename character varying(1024),
    sequencetype character varying(256),
    seqstring text,
    sequencedescription text,
    sequencetopology character varying(32) DEFAULT 'linear'::character varying,
    seqlength integer,
    sequenceurl character varying(2048),
    seqcomment character varying(2048),
    gi integer,
    fnindex_accession character varying(2048),
    fnindex_id character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 115)),
    CONSTRAINT "$2" CHECK ((((sequencetopology)::text = ('linear'::character varying)::text) OR ((sequencetopology)::text = ('circular'::character varying)::text)))
)
INHERITS (ob);


ALTER TABLE public.biosequenceob OWNER TO agrbrdf;

--
-- Name: biosubjectfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosubjectfact (
    biosubjectob integer NOT NULL,
    factnamespace character varying(256),
    attributedate date,
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.biosubjectfact OWNER TO agrbrdf;

--
-- Name: biosubjectob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosubjectob (
    subjectname character varying(1024),
    subjectspeciesname character varying(1024),
    subjecttaxon integer,
    strain character varying(1024),
    subjectdescription text,
    dob date,
    sex character varying(5),
    CONSTRAINT "$2" CHECK ((obtypeid = 85))
)
INHERITS (ob);


ALTER TABLE public.biosubjectob OWNER TO agrbrdf;

--
-- Name: blastn_results; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE blastn_results (
    runname character varying(30),
    querylength integer,
    queryid character varying(256),
    queryidindex character varying(256),
    hitid character varying(256),
    strand character varying(20),
    hitlength integer,
    description text,
    score double precision,
    evalue double precision,
    alignidentities integer,
    alignoverlaps integer,
    alignmismatches integer,
    aligngaps integer,
    qstart integer,
    qstop integer,
    hstart integer,
    hstop integer,
    keywords character varying(10),
    pctidentity double precision,
    species character varying(30),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.blastn_results OWNER TO agrbrdf;

--
-- Name: blastx_results; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE blastx_results (
    runname character varying(30),
    querylength integer,
    queryid character varying(128),
    hitid character varying(30),
    frame integer,
    hitlength integer,
    description text,
    score double precision,
    evalue double precision,
    alignidentities integer,
    alignoverlaps integer,
    alignpositives integer,
    aligngaps integer,
    qstart integer,
    qstop integer,
    hstart integer,
    hstop integer,
    keywords character varying(10),
    pctidentity double precision,
    species character varying(30),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.blastx_results OWNER TO agrbrdf;

--
-- Name: bovine_est_entropies; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE bovine_est_entropies (
    estname character varying(20),
    btrefseq_agbovine_csv double precision,
    bgisheep_agbovine_csv double precision,
    bovinevelevetse_agbovine_csv double precision,
    btau42_agbovine_csv double precision,
    btau461_agbovine_csv double precision,
    cs34_agbovine_csv double precision,
    cs39_agbovine_csv double precision,
    dfcibt_agbovine_csv double precision,
    dfcioa_agbovine_csv double precision,
    umd2_agbovine_csv double precision,
    umd3_agbovine_csv double precision
);


ALTER TABLE public.bovine_est_entropies OWNER TO agrbrdf;

--
-- Name: bt4wgsnppanel_v6_3cmarkernames; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE bt4wgsnppanel_v6_3cmarkernames (
    markerset_id integer,
    index integer,
    name character varying(40),
    onchipname character varying(40),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.bt4wgsnppanel_v6_3cmarkernames OWNER TO agrbrdf;

--
-- Name: commentlink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE commentlink (
    commentob integer NOT NULL,
    ob integer NOT NULL,
    commentdate date DEFAULT now(),
    commentby character varying(256),
    style_bgcolour character varying(64) DEFAULT '#99EE99'::character varying
);


ALTER TABLE public.commentlink OWNER TO agrbrdf;

--
-- Name: commentob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE commentob (
    commentstring text NOT NULL,
    commenttype character varying(1024),
    visibility character varying(32) DEFAULT 'public'::character varying,
    commentedob integer,
    voptypeid integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 40))
)
INHERITS (ob);


ALTER TABLE public.commentob OWNER TO agrbrdf;

--
-- Name: cpgfragmentsneargenes; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE cpgfragmentsneargenes (
    cpg_uniqueid character varying(30),
    frag_uniqueid character varying(30),
    refseq character varying(20),
    transcriptionstart integer,
    transcriptionend integer,
    strand character varying(10),
    name2 character varying(30),
    datasourceob integer,
    voptypeid integer,
    fragstart integer,
    fragstop integer
);


ALTER TABLE public.cpgfragmentsneargenes OWNER TO agrbrdf;

--
-- Name: cpgfragmentsneargenes_bakup; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE cpgfragmentsneargenes_bakup (
    cpg_uniqueid character varying(30),
    frag_uniqueid character varying(30),
    refseq character varying(20),
    transcriptionstart integer,
    transcriptionend integer,
    strand character varying(10),
    name2 character varying(30),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.cpgfragmentsneargenes_bakup OWNER TO agrbrdf;

--
-- Name: cs34clusterpaperdata; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE cs34clusterpaperdata (
    contig character varying(20),
    refseq character varying(20),
    gene_name character varying(20),
    blast_e_value character varying(20),
    gnf_atlas_2_data character varying(10),
    total_no__of_ests_in_contig integer,
    number_of_contigs_in_cluster integer,
    cluster_number integer,
    cluster_name character varying(20),
    datasourceob integer,
    voptypeid integer,
    contigname character varying(64)
);


ALTER TABLE public.cs34clusterpaperdata OWNER TO agrbrdf;

--
-- Name: data_set_1_genstat_results_180908; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE data_set_1_genstat_results_180908 (
    probes character varying(20),
    intensity double precision,
    est_1_ double precision,
    est_2_ double precision,
    est_3_ double precision,
    df integer,
    res_sd double precision,
    dbias double precision,
    se_1_ double precision,
    se_2_ double precision,
    se_3_ double precision,
    tval_1_ double precision,
    tval_2_ double precision,
    tval_3_ double precision,
    prob_1_ double precision,
    prob_2_ double precision,
    prob_3_ double precision,
    cont1ghvc double precision,
    cont2atrvc double precision,
    cont3atrvgh double precision,
    secont_1_ double precision,
    secont_2_ double precision,
    secont_3_ double precision,
    ctval_1_ double precision,
    ctval_2_ double precision,
    ctval_3_ double precision,
    cprob_1_ double precision,
    cprob_2_ double precision,
    cprob_3_ double precision,
    mod_sd double precision,
    mtval_1_ double precision,
    mtval_2_ double precision,
    mtval_3_ double precision,
    mcprob_1_ double precision,
    mcprob_2_ double precision,
    mcprob_3_ double precision,
    gene_id character varying(20),
    foldgh1 double precision,
    foldat1 double precision,
    foldgh2 double precision,
    foldat2 double precision,
    voptypeid integer,
    datasourceob integer,
    dataset character varying(20),
    fold double precision,
    prob double precision,
    intens double precision
);


ALTER TABLE public.data_set_1_genstat_results_180908 OWNER TO agrbrdf;

--
-- Name: data_set_2_r_results_180908; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE data_set_2_r_results_180908 (
    gene_id character varying(20),
    id__r integer,
    gene_name character varying(20),
    log_ratio double precision,
    absolute_log_ratio double precision,
    intensity double precision,
    fold_change double precision,
    biological_fold_change double precision,
    absolute_biological_fold_change double precision,
    raw_intensity double precision,
    simple_p_value double precision,
    moderated_p_value double precision,
    fdr double precision,
    log_mod_p_ double precision,
    log_fdr_ double precision,
    odds double precision,
    detail_scan_rank integer,
    no_dye_effect_fitted_scan_rank integer,
    no__good_spots integer,
    filter character varying(10),
    scan character varying(10),
    datasourceob integer,
    voptypeid integer,
    dataset character varying(20)
);


ALTER TABLE public.data_set_2_r_results_180908 OWNER TO agrbrdf;

--
-- Name: databasesearchobservation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE databasesearchobservation (
    databasesearchstudy integer NOT NULL,
    querysequence integer NOT NULL,
    hitsequence integer NOT NULL,
    queryxreflsid character varying(2048),
    querylength numeric(12,0),
    hitxreflsid character varying(2048),
    hitdescription text,
    hitlength numeric(12,0),
    hitevalue double precision,
    hitpvalue double precision,
    rawsearchresult text,
    observationcomment character varying(2048),
    userflags character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 325))
)
INHERITS (op);


ALTER TABLE public.databasesearchobservation OWNER TO agrbrdf;

--
-- Name: databasesearchstudy; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE databasesearchstudy (
    biodatabaseob integer,
    bioprotocolob integer,
    runby character varying(256),
    rundate date,
    studycomment character varying(2048),
    studytype character varying(128),
    studydescription character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 320))
)
INHERITS (op);


ALTER TABLE public.databasesearchstudy OWNER TO agrbrdf;

--
-- Name: datasourcefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE datasourcefact (
    datasourceob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.datasourcefact OWNER TO agrbrdf;

--
-- Name: datasourcelist; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE datasourcelist (
    listname character varying(256) NOT NULL,
    maxmembership integer,
    listcomment character varying(1024),
    CONSTRAINT datasourcelist_obtypeid_check CHECK ((obtypeid = 550))
)
INHERITS (ob);


ALTER TABLE public.datasourcelist OWNER TO agrbrdf;

--
-- Name: datasourcelistmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE datasourcelistmembershiplink (
    datasourcelist integer NOT NULL,
    datasourceob integer NOT NULL,
    inclusioncomment character varying(64),
    listorder integer,
    addeddate date DEFAULT now(),
    addedby character varying(256)
);


ALTER TABLE public.datasourcelistmembershiplink OWNER TO agrbrdf;

--
-- Name: datasourceob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE datasourceob (
    datasourcename character varying(1024),
    datasourcetype character varying(256),
    datasupplier character varying(2048),
    physicalsourceuri character varying(2048),
    datasupplieddate date,
    datasourcecomment text,
    numberoffiles integer,
    datasourcecontent text,
    dynamiccontentmethod character varying(256),
    uploadsourceuri character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 125))
)
INHERITS (ob);


ALTER TABLE public.datasourceob OWNER TO agrbrdf;

--
-- Name: displayfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE displayfunction (
    ob integer NOT NULL,
    datasourceob integer,
    displayprocedureob integer NOT NULL,
    functioncomment character varying(1024),
    invocation text,
    invocationorder integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 145))
)
INHERITS (op);


ALTER TABLE public.displayfunction OWNER TO agrbrdf;

--
-- Name: displayprocedureob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE displayprocedureob (
    procedurename character varying(1024),
    author character varying(2048),
    authordate date,
    sourcecode text,
    procedurecomment text,
    invocation text,
    proceduredescription character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 140))
)
INHERITS (ob);


ALTER TABLE public.displayprocedureob OWNER TO agrbrdf;

--
-- Name: fastq_links_temp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE fastq_links_temp (
    filename character varying(40)
);


ALTER TABLE public.fastq_links_temp OWNER TO agrbrdf;

--
-- Name: gbs_sample_name_patch_temp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gbs_sample_name_patch_temp (
    samplename character varying(20),
    sample character varying(10),
    lib character varying(10)
);


ALTER TABLE public.gbs_sample_name_patch_temp OWNER TO agrbrdf;

--
-- Name: gbs_sampleid_history_fact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gbs_sampleid_history_fact (
    biosampleob integer NOT NULL,
    sample character varying(32),
    qc_sampleid character varying(32),
    comment character varying(256),
    createddate date DEFAULT now(),
    createdby character varying(256),
    voptypeid integer
);


ALTER TABLE public.gbs_sampleid_history_fact OWNER TO agrbrdf;

--
-- Name: gbs_yield_import_temp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gbs_yield_import_temp (
    run character varying(64),
    sqname character varying(32),
    sampleid character varying(32),
    flowcell character varying(32),
    lane character varying(32),
    sqnumber character varying(32),
    tag_count character varying(32),
    read_count character varying(32),
    callrate character varying(32),
    sampdepth character varying(32),
    seqid character varying(64),
    matched integer,
    cohort character varying(128)
);


ALTER TABLE public.gbs_yield_import_temp OWNER TO agrbrdf;

--
-- Name: keyfile_factidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE keyfile_factidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.keyfile_factidseq OWNER TO agrbrdf;

--
-- Name: gbskeyfilefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gbskeyfilefact (
    factid integer DEFAULT nextval('keyfile_factidseq'::regclass) NOT NULL,
    biosampleob integer NOT NULL,
    flowcell character varying(32),
    lane integer,
    barcode character varying(32),
    sample character varying(64),
    platename character varying(32),
    platerow character varying(32),
    platecolumn integer,
    libraryprepid integer,
    counter integer,
    comment character varying(256),
    enzyme character varying(32),
    species character varying(256),
    numberofbarcodes character varying(4),
    bifo character varying(256),
    fastq_link character varying(256),
    createddate date DEFAULT now(),
    createdby character varying(256),
    voptypeid integer,
    control character varying(64),
    barcodedsampleob integer,
    subjectname character varying(64),
    windowsize character varying(32),
    gbs_cohort character varying(64),
    qc_cohort character varying(128),
    qc_sampleid character varying(32),
    refgenome_bwa_indexes character varying(1024),
    refgenome_blast_indexes character varying(1024),
    biosubjectob integer
);


ALTER TABLE public.gbskeyfilefact OWNER TO agrbrdf;

--
-- Name: gbskeyfilefact_backup25102016; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gbskeyfilefact_backup25102016 (
    factid integer,
    biosampleob integer,
    flowcell character varying(32),
    lane integer,
    barcode character varying(32),
    sample character varying(32),
    platename character varying(32),
    platerow character varying(32),
    platecolumn integer,
    libraryprepid integer,
    counter integer,
    comment character varying(256),
    enzyme character varying(32),
    species character varying(256),
    numberofbarcodes character varying(4),
    bifo character varying(256),
    fastq_link character varying(256),
    createddate date,
    createdby character varying(256),
    voptypeid integer,
    control character varying(64),
    barcodedsampleob integer
);


ALTER TABLE public.gbskeyfilefact_backup25102016 OWNER TO agrbrdf;

--
-- Name: gbsyf_factidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE gbsyf_factidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gbsyf_factidseq OWNER TO agrbrdf;

--
-- Name: gbsyieldfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gbsyieldfact (
    factid integer DEFAULT nextval('gbsyf_factidseq'::regclass) NOT NULL,
    biosamplelist integer NOT NULL,
    biosampleob integer,
    sqname character varying(32),
    sampleid character varying(64),
    flowcell character varying(32),
    lane integer,
    sqnumber integer,
    tag_count integer,
    read_count integer,
    callrate double precision,
    sampdepth double precision,
    cohort character varying(128)
);


ALTER TABLE public.gbsyieldfact OWNER TO agrbrdf;

--
-- Name: gene2accession; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gene2accession (
    tax_id integer,
    geneid character varying(128),
    status character varying(64),
    rna_nucleotide_accession character varying(64),
    rna_nucleotide_gi character varying(32),
    protein_accession character varying(64),
    protein_gi character varying(32),
    genomic_nucleotide_accession character varying(64),
    genomic_nucleotide_gi character varying(32),
    start_position_on_the_genomic_accession character varying(32),
    end_position_on_the_genomic_accession character varying(32),
    orientation character varying(8),
    assembly character varying(64),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.gene2accession OWNER TO agrbrdf;

--
-- Name: gene_info; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gene_info (
    tax_id integer,
    geneid character varying(128),
    symbol character varying(64),
    locustag character varying(64),
    synonyms character varying(1024),
    dbxrefs character varying(1024),
    chromosome character varying(32),
    map_location character varying(64),
    description text,
    type_of_gene character varying(64),
    symbol_from_nomenclature_authority character varying(128),
    full_name_from_nomenclature_authority character varying(4196),
    nomenclature_status character varying(128),
    other_designations character varying(8192),
    modification_date character varying(16),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.gene_info OWNER TO agrbrdf;

--
-- Name: geneexpressionstudy; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneexpressionstudy (
    biosamplelist integer NOT NULL,
    labresourcelist integer,
    labresourceob integer,
    bioprotocolob integer,
    studytype character varying(128),
    studydescription text,
    studyname character varying(128),
    CONSTRAINT "$1" CHECK ((obtypeid = 240))
)
INHERITS (op);


ALTER TABLE public.geneexpressionstudy OWNER TO agrbrdf;

--
-- Name: geneexpressionstudy_backup01032009; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneexpressionstudy_backup01032009 (
    obid integer,
    obtypeid integer,
    xreflsid character varying(2048),
    createddate date,
    createdby character varying(256),
    lastupdateddate date,
    lastupdatedby character varying(256),
    checkedout boolean,
    checkedoutby character varying(256),
    checkoutdate date,
    obkeywords character varying(4096),
    statuscode integer,
    voptypeid integer,
    biosamplelist integer,
    labresourcelist integer,
    labresourceob integer,
    bioprotocolob integer,
    studytype character varying(128),
    studydescription text,
    studyname character varying(128)
);


ALTER TABLE public.geneexpressionstudy_backup01032009 OWNER TO agrbrdf;

--
-- Name: geneexpressionstudyfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneexpressionstudyfact (
    geneexpressionstudy integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.geneexpressionstudyfact OWNER TO agrbrdf;

--
-- Name: geneproductlink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneproductlink (
    geneticob integer NOT NULL,
    biosequenceob integer NOT NULL,
    producttype character varying(1024),
    evidence text,
    productcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 201))
)
INHERITS (op);


ALTER TABLE public.geneproductlink OWNER TO agrbrdf;

--
-- Name: generegulationlink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE generegulationlink (
    geneticob integer NOT NULL,
    biosequenceob integer NOT NULL,
    regulationtype character varying(1024),
    evidence text,
    regulationcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 202))
)
INHERITS (op);


ALTER TABLE public.generegulationlink OWNER TO agrbrdf;

--
-- Name: geneticexpressionfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticexpressionfact (
    geneticob integer,
    biosequenceob integer,
    expressionmapname character varying(2048),
    expressionmaplocus character varying(128),
    speciesname character varying(256),
    speciestaxid integer,
    expressionamount double precision,
    evidence text,
    evidencepvalue double precision,
    CONSTRAINT "$1" CHECK ((obtypeid = 195))
)
INHERITS (op);


ALTER TABLE public.geneticexpressionfact OWNER TO agrbrdf;

--
-- Name: geneticfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticfact (
    geneticob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096),
    CONSTRAINT "$1" CHECK ((obtypeid = 200))
)
INHERITS (op);


ALTER TABLE public.geneticfact OWNER TO agrbrdf;

--
-- Name: geneticfunctionfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticfunctionfact (
    geneticob integer NOT NULL,
    goterm character varying(2048),
    godescription character varying(2048),
    functiondescription character varying(2048),
    functioncomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 190))
)
INHERITS (op);


ALTER TABLE public.geneticfunctionfact OWNER TO agrbrdf;

--
-- Name: geneticlocationfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticlocationfact (
    geneticob integer,
    biosequenceob integer,
    genetictestfact integer,
    mapname character varying(2048),
    maptype character varying(2048) DEFAULT 'sequence'::character varying,
    mapunit character varying(128) DEFAULT 'bases'::character varying,
    speciesname character varying(256),
    speciestaxid integer,
    entrezgeneid integer,
    locusname character varying(256),
    locustag character varying(128),
    locussynonyms character varying(2048),
    chromosomename0 character varying(32),
    strand character varying(3),
    locationstart numeric(12,0),
    locationstop numeric(12,0),
    locationstring character varying(2048),
    regionsize numeric(12,0),
    markers character varying(2048),
    locationdescription character varying(2048),
    othermaplocation1 character varying(128),
    evidence text,
    evidencescore double precision,
    evidencepvalue double precision,
    chromosomename character varying(128),
    mapobid integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 175)),
    CONSTRAINT "$2" CHECK ((((((maptype)::text = ('linkage'::character varying)::text) OR ((maptype)::text = ('rh'::character varying)::text)) OR ((maptype)::text = ('sequence'::character varying)::text)) OR ((maptype)::text = ('physical'::character varying)::text))),
    CONSTRAINT "$3" CHECK ((((mapunit)::text = ('centiMorgans'::character varying)::text) OR ((mapunit)::text = ('bases'::character varying)::text)))
)
INHERITS (op);


ALTER TABLE public.geneticlocationfact OWNER TO agrbrdf;

--
-- Name: geneticlocationlist; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticlocationlist (
    listname character varying(256) NOT NULL,
    maxmembership integer,
    listcomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 180))
)
INHERITS (ob);


ALTER TABLE public.geneticlocationlist OWNER TO agrbrdf;

--
-- Name: geneticlocationlistmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticlocationlistmembershiplink (
    geneticlocationlist integer NOT NULL,
    geneticlocationfact integer NOT NULL,
    inclusioncomment character varying(64),
    addeddate date DEFAULT now(),
    addedby character varying(256)
);


ALTER TABLE public.geneticlocationlistmembershiplink OWNER TO agrbrdf;

--
-- Name: geneticob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticob (
    geneticobname character varying(256),
    geneticobtype character varying(256),
    geneticobdescription text,
    geneticobsymbols character varying(2048),
    obcomment character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 160))
)
INHERITS (ob);


ALTER TABLE public.geneticob OWNER TO agrbrdf;

--
-- Name: geneticoblist; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticoblist (
    listname character varying(256) NOT NULL,
    maxmembership integer,
    listcomment character varying(1024),
    listtype character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 165))
)
INHERITS (ob);


ALTER TABLE public.geneticoblist OWNER TO agrbrdf;

--
-- Name: geneticoblistmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticoblistmembershiplink (
    geneticoblist integer NOT NULL,
    geneticob integer NOT NULL,
    inclusioncomment character varying(64),
    addeddate date DEFAULT now(),
    addedby character varying(256)
);


ALTER TABLE public.geneticoblistmembershiplink OWNER TO agrbrdf;

--
-- Name: genetictestfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genetictestfact (
    labresourceob integer NOT NULL,
    accession character varying(256),
    testtype character varying(1024),
    locusname character varying(256),
    variation character varying(1024),
    testdescription character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 305))
)
INHERITS (op);


ALTER TABLE public.genetictestfact OWNER TO agrbrdf;

--
-- Name: genetictestfact2; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genetictestfact2 (
    genetictestfact integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.genetictestfact2 OWNER TO agrbrdf;

--
-- Name: genotype_animalid_extract; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genotype_animalid_extract (
    sampleid character varying(50),
    animalid integer
);


ALTER TABLE public.genotype_animalid_extract OWNER TO agrbrdf;

--
-- Name: genotypeobservation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genotypeobservation (
    genotypestudy integer,
    genetictestfact integer,
    observationdate date,
    genotypeobserved character varying(256),
    genotypeobserveddescription character varying(1024),
    finalgenotype character varying(256),
    finalgenotypedescription character varying(1024),
    observationcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 300))
)
INHERITS (op);


ALTER TABLE public.genotypeobservation OWNER TO agrbrdf;

--
-- Name: genotypeobservationfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genotypeobservationfact (
    genotypeobservation integer NOT NULL,
    factnamespace character varying(256),
    attributedate date,
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.genotypeobservationfact OWNER TO agrbrdf;

--
-- Name: genotypes; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genotypes (
    sample_id character varying(32),
    snp_name character varying(64),
    allele1_forward character varying(10),
    allele2_forward character varying(10),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.genotypes OWNER TO agrbrdf;

--
-- Name: genotypestudy; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genotypestudy (
    biosamplelist integer,
    biosampleob integer,
    labresourcelist integer,
    labresourceob integer,
    bioprotocolob integer NOT NULL,
    studytype character varying(128),
    CONSTRAINT "$1" CHECK ((obtypeid = 290))
)
INHERITS (op);


ALTER TABLE public.genotypestudy OWNER TO agrbrdf;

--
-- Name: genotypestudyfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genotypestudyfact (
    genotypestudy integer NOT NULL,
    factnamespace character varying(256),
    attributedate date,
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.genotypestudyfact OWNER TO agrbrdf;

--
-- Name: geosubmissiondata; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geosubmissiondata (
    recnum integer,
    sourcefile character varying(128),
    id_ref integer,
    gene_name character varying(64),
    spot_id character varying(64),
    value double precision,
    ch1_sig_mean double precision,
    ch1_bkd_mean double precision,
    ch2_sig_mean double precision,
    ch2_bkd_mean double precision,
    datasourceob integer,
    voptypeid integer,
    poolid1 character varying(32),
    genesymbol character varying(30),
    norm_intensity double precision,
    filerecnum integer,
    control_type integer,
    gisfeatnonunifol integer,
    risfeatpopnol integer,
    risfeatnonunifol integer,
    gisfeatpopnol integer
);


ALTER TABLE public.geosubmissiondata OWNER TO agrbrdf;

--
-- Name: gpl3802_annotation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gpl3802_annotation (
    probe_set_id character varying(30),
    genechip_array character varying(20),
    species_scientific_name character varying(20),
    annotation_date character varying(20),
    sequence_type character varying(20),
    sequence_source character varying(40),
    transcript_idarray_design character varying(20),
    target_description character varying(550),
    representative_public_id character varying(30),
    archival_unigene_cluster character varying(10),
    unigene_id character varying(50),
    genome_version character varying(10),
    alignments character varying(10),
    gene_title character varying(250),
    gene_symbol character varying(100),
    chromosomal_location character varying(10),
    unigene_cluster_type character varying(20),
    ensembl character varying(10),
    entrez_gene character varying(80),
    swissprot character varying(450),
    ec character varying(10),
    omim character varying(10),
    refseq_protein_id character varying(10),
    refseq_transcript_id character varying(10),
    flybase character varying(10),
    agi character varying(10),
    wormbase character varying(10),
    mgi_name character varying(10),
    rgd_name character varying(10),
    sgd_accession_number character varying(10),
    gene_ontology_biological_process character varying(1300),
    gene_ontology_cellular_component character varying(560),
    gene_ontology_molecular_function character varying(1660),
    pathway character varying(10),
    interpro character varying(350),
    trans_membrane character varying(580),
    qtl character varying(10),
    annotation_description character varying(200),
    annotation_transcript_cluster character varying(4140),
    transcript_assignments character varying(29950),
    annotation_notes character varying(15990),
    uniref_hit_accession__harvest_3over2010 character varying(100),
    uniref_hit_description__harvest_3over2010 character varying(170),
    uniref_e_value__harvest_3over2010 character varying(120),
    go_molecular_function_ids__agrigo_3over2010 character varying(160),
    go_molecular_function_terms__agrigo_3over2010 character varying(400),
    go_biological_process_ids__agrigo_3over2010 character varying(460),
    go_biological_process_terms__agrigo_3over2010 character varying(1190),
    go_cellular_component_ids__agrigo_3over2010 character varying(120),
    go_cellular_component_terms__agrigo_3over2010 character varying(200),
    go_missing_info_ids__agrigo_3over2010 character varying(30),
    go_missing_info_terms__agrigo_3over2010 character varying(40),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.gpl3802_annotation OWNER TO agrbrdf;

--
-- Name: gpl7083_34008annotation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gpl7083_34008annotation (
    id integer,
    col integer,
    "row" integer,
    name character varying(20),
    spot_id character varying(20),
    control_type character varying(10),
    refseq character varying(20),
    gb_acc character varying(20),
    locuslink_id character varying(10),
    gene_symbol character varying(20),
    gene_name character varying(160),
    unigene_id character varying(10),
    ensembl_id character varying(20),
    tigr_id character varying(10),
    accession_string character varying(100),
    chromosomal_location character varying(10),
    cytoband character varying(10),
    description character varying(210),
    go_id character varying(3300),
    sequence character varying(70),
    datasourceob integer,
    voptypeid integer,
    human_refseqacc character varying(32),
    human_refseqevalue double precision,
    human_refseqdescription character varying(4096),
    human_refseqgenesymbol character varying(32),
    human_refseqgenedescription character varying(4096),
    ensbiomart_geneid integer,
    ensbiomart_genesymbol character varying(32),
    ensbiomart_genedescription character varying(4096),
    human_refseqgeneid integer
);


ALTER TABLE public.gpl7083_34008annotation OWNER TO agrbrdf;

--
-- Name: harvestwheatchip_annotation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE harvestwheatchip_annotation (
    all_probes character varying(30),
    probe_set_name_found character varying(30),
    exemplar_assembly character varying(10),
    exemplar_unigene character varying(20),
    pre_polya_trim_length integer,
    members integer,
    num__unigenes integer,
    unigenes_represented character varying(910),
    uniprot_accn character varying(30),
    uniprot_e_score double precision,
    uniprot_desc character varying(170),
    rice_accn character varying(20),
    rice_e_score double precision,
    rice_chr integer,
    rice_5prime integer,
    rice_3prime integer,
    rice_desc character varying(130),
    arab_accn character varying(20),
    arab_e_score double precision,
    arab_chr character varying(10),
    arab_5prime integer,
    arab_3prime integer,
    arab_desc character varying(140),
    brachy_accn character varying(20),
    brachy_e_score double precision,
    brachy_chr character varying(10),
    brachy_5prime integer,
    brachy_3prime integer,
    brachy_desc character varying(90),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.harvestwheatchip_annotation OWNER TO agrbrdf;

--
-- Name: hg18_cpg_location; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hg18_cpg_location (
    chrom character varying(20),
    chromstart integer,
    chromend integer,
    name character varying(10),
    length integer,
    cpgnum integer,
    gcnum integer,
    percpg double precision,
    pergc double precision,
    obsexp double precision,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.hg18_cpg_location OWNER TO agrbrdf;

--
-- Name: hg18_cpg_mspi_overlap; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hg18_cpg_mspi_overlap (
    cpg_uniqueid character varying(30),
    chromstart integer,
    chromend integer,
    cpg_length integer,
    cpg_name character varying(10),
    frag_uniqueid character varying(30),
    start integer,
    stop integer,
    frag_length integer,
    datasourceob integer,
    voptypeid integer,
    chrom character varying(32)
);


ALTER TABLE public.hg18_cpg_mspi_overlap OWNER TO agrbrdf;

--
-- Name: hg18_cpg_mspi_overlap_bakup; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hg18_cpg_mspi_overlap_bakup (
    cpg_uniqueid character varying(30),
    chromstart integer,
    chromend integer,
    cpg_length integer,
    cpg_name character varying(10),
    frag_uniqueid character varying(30),
    start integer,
    stop integer,
    frag_length integer,
    datasourceob integer,
    voptypeid integer,
    chrom character varying(32)
);


ALTER TABLE public.hg18_cpg_mspi_overlap_bakup OWNER TO agrbrdf;

--
-- Name: hg18_mspi_digest; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hg18_mspi_digest (
    chrom character varying(10),
    accession character varying(40),
    start integer,
    stop integer,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.hg18_mspi_digest OWNER TO agrbrdf;

--
-- Name: hg18_refgenes_location; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hg18_refgenes_location (
    name character varying(20),
    chrom character varying(20),
    strand character varying(10),
    transcriptionstart integer,
    transcriptionend integer,
    cdsstart integer,
    cdsend integer,
    id integer,
    name2 character varying(30),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.hg18_refgenes_location OWNER TO agrbrdf;

--
-- Name: hg18uniquereads; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hg18uniquereads (
    uniquetype character varying(20),
    queryfrag character varying(64),
    mappedtofrag character varying(64),
    sequencedfrom character varying(32),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.hg18uniquereads OWNER TO agrbrdf;

--
-- Name: samplesheet_factidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE samplesheet_factidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.samplesheet_factidseq OWNER TO agrbrdf;

--
-- Name: hiseqsamplesheetfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hiseqsamplesheetfact (
    factid integer DEFAULT nextval('samplesheet_factidseq'::regclass) NOT NULL,
    biosamplelist integer NOT NULL,
    fcid character varying(32),
    lane integer,
    sampleid character varying(32),
    sampleref character varying(32),
    sampleindex character varying(1024),
    description character varying(256),
    control character varying(32),
    recipe integer,
    operator character varying(256),
    sampleproject character varying(256),
    createddate date DEFAULT now(),
    createdby character varying(256),
    voptypeid integer,
    sampleplate character varying(64),
    samplewell character varying(64),
    downstream_processing character varying(64),
    basespace_project character varying(256)
);


ALTER TABLE public.hiseqsamplesheetfact OWNER TO agrbrdf;

--
-- Name: humanplacentalorthologs; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE humanplacentalorthologs (
    orthogene character varying(2048),
    humanplacentalortholog integer
);


ALTER TABLE public.humanplacentalorthologs OWNER TO agrbrdf;

--
-- Name: importfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE importfunction (
    ob integer,
    datasourceob integer NOT NULL,
    importprocedureob integer NOT NULL,
    importerrors text,
    processinginstructions text,
    notificationaddresses text,
    submissionreasons text,
    functioncomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 135))
)
INHERITS (op);


ALTER TABLE public.importfunction OWNER TO agrbrdf;

--
-- Name: importfunctionfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE importfunctionfact (
    importfunction integer NOT NULL,
    factnamespace character varying(256),
    attributedate date,
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.importfunctionfact OWNER TO agrbrdf;

--
-- Name: importprocedureob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE importprocedureob (
    procedurename character varying(1024),
    author character varying(2048),
    authordate date,
    sourcecode text,
    procedurecomment text,
    importdatasourceinvocation text,
    displaydatasourceinvocation text,
    CONSTRAINT "$1" CHECK ((obtypeid = 130))
)
INHERITS (ob);


ALTER TABLE public.importprocedureob OWNER TO agrbrdf;

--
-- Name: junk; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE junk (
    obid integer,
    xreflsid character varying(2048),
    seqlength integer,
    contigdepth bigint
);


ALTER TABLE public.junk OWNER TO agrbrdf;

--
-- Name: junk1; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE junk1 (
    obid integer,
    xreflsid text,
    seqlength integer,
    contigdepth bigint,
    height integer,
    width integer,
    contignumber text,
    datasourcelsid text
);


ALTER TABLE public.junk1 OWNER TO agrbrdf;

--
-- Name: keyfile_temp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE keyfile_temp (
    flowcell character varying(32),
    lane integer,
    barcode character varying(32),
    sample character varying(64),
    platename character varying(32),
    platerow character varying(32),
    platecolumn integer,
    libraryprepid integer,
    counter integer,
    comment character varying(256),
    enzyme character varying(32),
    species character varying(256),
    numberofbarcodes character varying(4),
    bifo character varying(256),
    fastq_link character varying(256),
    control character varying(64),
    windowsize character varying(32),
    gbs_cohort character varying(32)
);


ALTER TABLE public.keyfile_temp OWNER TO agrbrdf;

--
-- Name: keyfile_temp_nofastq; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE keyfile_temp_nofastq (
    flowcell character varying(32),
    lane integer,
    barcode character varying(32),
    sample character varying(32),
    platename character varying(32),
    platerow character varying(32),
    platecolumn integer,
    libraryprepid integer,
    counter integer,
    comment character varying(256),
    enzyme character varying(32),
    species character varying(256),
    numberofbarcodes character varying(4),
    bifo character varying(256)
);


ALTER TABLE public.keyfile_temp_nofastq OWNER TO agrbrdf;

--
-- Name: labresourcefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE labresourcefact (
    labresourceob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.labresourcefact OWNER TO agrbrdf;

--
-- Name: labresourcelist; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE labresourcelist (
    listname character varying(256) NOT NULL,
    maxmembership integer,
    listcomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 75))
)
INHERITS (ob);


ALTER TABLE public.labresourcelist OWNER TO agrbrdf;

--
-- Name: labresourcelistmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE labresourcelistmembershiplink (
    labresourcelist integer NOT NULL,
    labresourceob integer NOT NULL,
    inclusioncomment character varying(64),
    addeddate date DEFAULT now(),
    addedby character varying(256)
);


ALTER TABLE public.labresourcelistmembershiplink OWNER TO agrbrdf;

--
-- Name: labresourceob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE labresourceob (
    resourcename character varying(1024),
    resourcetype character varying(256) NOT NULL,
    resourcesequence text,
    forwardprimersequence text,
    reverseprimersequence text,
    resourceseqlength integer,
    resourcedate date,
    resourcedescription text,
    supplier character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 70))
)
INHERITS (ob);


ALTER TABLE public.labresourceob OWNER TO agrbrdf;

--
-- Name: librarysequencingfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE librarysequencingfact (
    librarysequencingfunction integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.librarysequencingfact OWNER TO agrbrdf;

--
-- Name: librarysequencingfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE librarysequencingfunction (
    biolibraryob integer,
    datasourceob integer NOT NULL,
    bioprotocolob integer,
    labresourcelist integer,
    labresourceob integer,
    runby character varying(256),
    rundate date,
    functioncomment character varying(1024),
    CONSTRAINT librarysequencingfunction_obtypeid_check CHECK ((obtypeid = 500))
)
INHERITS (op);


ALTER TABLE public.librarysequencingfunction OWNER TO agrbrdf;

--
-- Name: licexpression1; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE licexpression1 (
    anml_key integer,
    inputfile character varying(64),
    affygene character varying(64),
    expression double precision,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.licexpression1 OWNER TO agrbrdf;

--
-- Name: licnormalisation1; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE licnormalisation1 (
    probeset character varying(30),
    lipid_pct double precision,
    crude_aa_pct double precision,
    true_aa_pct double precision,
    casein_pct double precision,
    lcts_pct double precision,
    ttl_solid_pct double precision,
    scc double precision,
    growth_hormone double precision,
    igf_1 double precision,
    insulin double precision,
    sire double precision,
    am_and_pm__average_milk_volume double precision,
    crude_aa_yield double precision,
    true_aa_yield double precision,
    casein_yield double precision,
    number_of_present_calls_over_all_254_slides integer,
    number_of_present_calls_for_just_the_tissue_samples character varying(10),
    analysisname character varying(32),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.licnormalisation1 OWNER TO agrbrdf;

--
-- Name: lindawheat1; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE lindawheat1 (
    id__r integer,
    gene_id character varying(30),
    log_ratio double precision,
    biological_fold_change double precision,
    moderated_p_value double precision,
    fdr double precision,
    flag1 integer,
    flag2 integer,
    log_ratio_1 double precision,
    fold_change double precision,
    biological_fold_change_1 double precision,
    absolute_biol_fold_change double precision,
    geomean_1 double precision,
    geomean_2 double precision,
    maximum_geomean double precision,
    simple_p_value double precision,
    moderated_p_value_1 double precision,
    fdr_1 double precision,
    logmod_p double precision,
    logfdr double precision,
    flag1_1 integer,
    flag2_1 integer,
    df_resid double precision,
    df_total double precision,
    scan_rank integer,
    pma_call__lj0001_wheat_cel character varying(10),
    pma_call__lj0002_wheat_cel character varying(10),
    pma_call__lj0003_wheat_cel character varying(10),
    pma_call__lj0004_wheat_cel character varying(10),
    pma_call__lj0005_wheat_cel character varying(10),
    pma_call__lj0006_wheat_cel character varying(10),
    genechip_array character varying(20),
    species_scientific_name character varying(20),
    annotation_date character varying(20),
    sequence_type character varying(20),
    sequence_source character varying(10),
    transcript_idarray_design character varying(20),
    target_description character varying(340),
    representative_public_id character varying(20),
    archival_unigene_cluster character varying(10),
    unigene_id character varying(30),
    genome_version character varying(10),
    alignments character varying(10),
    gene_title character varying(110),
    gene_symbol character varying(10),
    chromosomal_location character varying(10),
    unigene_cluster_type character varying(20),
    ensembl character varying(10),
    entrez_gene character varying(10),
    swissprot character varying(10),
    ec character varying(10),
    omim character varying(10),
    refseq_protein_id character varying(10),
    refseq_transcript_id character varying(10),
    flybase character varying(10),
    agi character varying(10),
    wormbase character varying(10),
    mgi_name character varying(10),
    rgd_name character varying(10),
    sgd_accession_number character varying(10),
    gene_ontology_biological_process character varying(10),
    gene_ontology_cellular_component character varying(80),
    gene_ontology_molecular_function character varying(70),
    pathway character varying(10),
    interpro character varying(10),
    trans_membrane character varying(50),
    qtl character varying(10),
    annotation_description character varying(180),
    annotation_transcript_cluster character varying(210),
    transcript_assignments character varying(2070),
    annotation_notes character varying(510),
    input_probe_set character varying(30),
    probe_set_name_found character varying(30),
    exemplar_assembly character varying(10),
    exemplar_unigene character varying(20),
    pre_polya_trim_length integer,
    members integer,
    num__unigenes integer,
    unigenes_represented character varying(40),
    uniprot_accn character varying(30),
    uniprot_e_score double precision,
    uniprot_desc character varying(170),
    rice_accn character varying(20),
    rice_e_score double precision,
    rice_chr integer,
    rice_5prime integer,
    rice_3prime integer,
    rice_desc character varying(100),
    arab_accn character varying(20),
    arab_e_score double precision,
    arab_chr integer,
    arab_5prime integer,
    arab_3prime integer,
    arab_desc character varying(140),
    heatmap_order_relative_to_data_sorted_by_transcript_id integer
);


ALTER TABLE public.lindawheat1 OWNER TO agrbrdf;

--
-- Name: lisafan_expt136_lowscan_no_bg_corr_delete01102008; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE lisafan_expt136_lowscan_no_bg_corr_delete01102008 (
    recnum integer,
    gene_name character varying(64),
    gene_id character varying(64),
    log_ratio double precision,
    absolute_log_ratio double precision,
    intensity double precision,
    fold_change double precision,
    biological_fold_change double precision,
    absolute_biological_fold_change double precision,
    raw_intensity double precision,
    simple_pvalue double precision,
    moderated_pvalue double precision,
    fdr double precision,
    log_mod_p double precision,
    log_fdr double precision,
    odds double precision,
    detail_scan_rank integer,
    high_scans_no_bg_corr_scan_rank integer,
    high_scans_normexp_scan_rank integer,
    low_scans_no_bg_corr_scan_rank integer,
    num_good_spots integer,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.lisafan_expt136_lowscan_no_bg_corr_delete01102008 OWNER TO agrbrdf;

--
-- Name: lisafanseriesnormalisation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE lisafanseriesnormalisation (
    recnum integer,
    gene_name character varying(64),
    log_ratio double precision,
    absolute_log_ratio double precision,
    intensity double precision,
    fold_change double precision,
    biological_fold_change double precision,
    absolute_biological_fold_change double precision,
    raw_intensity double precision,
    simple_pvalue double precision,
    moderated_pvalue double precision,
    fdr double precision,
    log_mod_p double precision,
    log_fdr double precision,
    odds double precision,
    detail_scan_rank double precision,
    high_scans_no_bg_corr_scan_rank double precision,
    high_scans_normexp_scan_rank double precision,
    low_scans_no_bg_corr_scan_rank double precision,
    num_good_spots integer,
    datasourceob integer,
    voptypeid integer,
    seriesname character varying(64)
);


ALTER TABLE public.lisafanseriesnormalisation OWNER TO agrbrdf;

--
-- Name: lisafanseriesnormalisation_backup23092008; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE lisafanseriesnormalisation_backup23092008 (
    recnum integer,
    gene_name character varying(64),
    log_ratio double precision,
    absolute_log_ratio double precision,
    intensity double precision,
    fold_change double precision,
    biological_fold_change double precision,
    absolute_biological_fold_change double precision,
    raw_intensity double precision,
    simple_pvalue double precision,
    moderated_pvalue double precision,
    fdr double precision,
    log_mod_p double precision,
    log_fdr double precision,
    odds double precision,
    detail_scan_rank double precision,
    high_scans_no_bg_corr_scan_rank double precision,
    high_scans_normexp_scan_rank double precision,
    low_scans_no_bg_corr_scan_rank double precision,
    num_good_spots integer,
    datasourceob integer,
    voptypeid integer,
    seriesname character varying(64)
);


ALTER TABLE public.lisafanseriesnormalisation_backup23092008 OWNER TO agrbrdf;

--
-- Name: list_tmp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE list_tmp (
    contig_name character varying(30)
);


ALTER TABLE public.list_tmp OWNER TO agrbrdf;

--
-- Name: listorderseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE listorderseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.listorderseq OWNER TO agrbrdf;

--
-- Name: lmf_factidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE lmf_factidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lmf_factidseq OWNER TO agrbrdf;

--
-- Name: listmembershipfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE listmembershipfact (
    factid integer DEFAULT nextval('lmf_factidseq'::regclass) NOT NULL,
    oblist integer NOT NULL,
    memberid character varying(2048),
    listorder integer DEFAULT nextval('listorderseq'::regclass),
    createddate date DEFAULT now(),
    createdby character varying(256),
    membershipcomment text,
    voptypeid integer
);


ALTER TABLE public.listmembershipfact OWNER TO agrbrdf;

--
-- Name: listmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE listmembershiplink (
    oblist integer NOT NULL,
    ob integer NOT NULL,
    obxreflsid character varying(2048),
    listorder integer DEFAULT nextval(('listorderseq'::text)::regclass),
    createddate date DEFAULT now(),
    createdby character varying(256),
    membershipcomment text,
    voptypeid integer
);


ALTER TABLE public.listmembershiplink OWNER TO agrbrdf;

--
-- Name: literaturereferencelink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE literaturereferencelink (
    ob integer NOT NULL,
    literaturereferenceob integer NOT NULL,
    linkcomment text
);


ALTER TABLE public.literaturereferencelink OWNER TO agrbrdf;

--
-- Name: literaturereferenceob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE literaturereferenceob (
    journalname character varying(2048) NOT NULL,
    volumename character varying(16),
    volnumber integer,
    voldate date,
    papertitle character varying(2048),
    authors character varying(4096),
    abstract text,
    ourcomments text,
    CONSTRAINT "$1" CHECK ((obtypeid = 60))
)
INHERITS (ob);


ALTER TABLE public.literaturereferenceob OWNER TO agrbrdf;

--
-- Name: miamefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE miamefact (
    microarraystudy integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.miamefact OWNER TO agrbrdf;

--
-- Name: microarrayfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE microarrayfact (
    labresourceob integer NOT NULL,
    arrayname character varying(256),
    arraycomment character varying(2048),
    gal_type character varying(256),
    gal_blockcount integer,
    gal_blocktype integer,
    gal_url character varying(512),
    gal_supplier character varying(512),
    gal_block1 character varying(512),
    CONSTRAINT microarrayfact_gal_block1 CHECK ((obtypeid = 230))
)
INHERITS (op);


ALTER TABLE public.microarrayfact OWNER TO agrbrdf;

--
-- Name: microarrayobservation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE microarrayobservation (
    microarraystudy integer NOT NULL,
    microarrayspotfact integer,
    gpr_block integer,
    gpr_column integer,
    gpr_row integer,
    gpr_name character varying(256),
    gpr_id character varying(256),
    gpr_dye1foregroundmean integer,
    gpr_dye1backgroundmean integer,
    gpr_dye2foregroundmean integer,
    gpr_dye2backgroundmean integer,
    gpr_logratio real,
    gpr_flags integer,
    gpr_autoflag integer,
    norm_logratio real,
    norm_dye1intensity real,
    norm_dye2intensity real,
    rawdatarecord text,
    observationcomment character varying(1024),
    affy_meanpm double precision,
    affy_meanmm double precision,
    affy_stddevpm double precision,
    affy_stddevmm double precision,
    affy_count integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 250))
)
INHERITS (op);


ALTER TABLE public.microarrayobservation OWNER TO agrbrdf;

--
-- Name: microarrayobservationfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE microarrayobservationfact (
    microarrayobservation integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.microarrayobservationfact OWNER TO agrbrdf;

--
-- Name: microarrayspotfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE microarrayspotfact (
    labresourceob integer NOT NULL,
    accession character varying(256),
    blocknumber integer,
    blockrow integer,
    blockcolumn integer,
    metarow integer,
    metacolumn integer,
    spotcomment character varying(2048),
    gal_block integer,
    gal_column integer,
    gal_row integer,
    gal_name character varying(256),
    gal_id character varying(128),
    gal_refnumber integer,
    gal_controltype character varying(32),
    gal_genename character varying(128),
    gal_tophit character varying(256),
    gal_description character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 235))
)
INHERITS (op);


ALTER TABLE public.microarrayspotfact OWNER TO agrbrdf;

--
-- Name: mylogger; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE mylogger (
    msgorder integer,
    msgtext text
);


ALTER TABLE public.mylogger OWNER TO agrbrdf;

--
-- Name: ob_obidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE ob_obidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ob_obidseq OWNER TO agrbrdf;

--
-- Name: oblist; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE oblist (
    listname character varying(256) NOT NULL,
    listtype character varying(128),
    listdefinition text,
    bookmark integer,
    maxmembership integer,
    currentmembership integer DEFAULT 0,
    listcomment character varying(1024),
    displayurl character varying(2048) DEFAULT 'ob.gif'::character varying,
    membershipvisibility character varying(32) DEFAULT 'public'::character varying,
    CONSTRAINT "$1" CHECK ((obtypeid = 20))
)
INHERITS (ob);


ALTER TABLE public.oblist OWNER TO agrbrdf;

--
-- Name: oblistfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE oblistfact (
    listob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.oblistfact OWNER TO agrbrdf;

--
-- Name: obstatus; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE obstatus (
    statuscode integer NOT NULL,
    statusname character varying(128) NOT NULL,
    statusdescription character varying(2048)
);


ALTER TABLE public.obstatus OWNER TO agrbrdf;

--
-- Name: TABLE obstatus; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON TABLE obstatus IS 'This table will be used to support object versioning, with previous versions having inactive 	status and 	linked to current versions via a link table';


--
-- Name: obtype; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE obtype (
    obtypeid integer DEFAULT nextval(('obtype_obtypeidseq'::text)::regclass) NOT NULL,
    displayname character varying(2048),
    uri character varying(2048),
    displayurl character varying(2048) DEFAULT 'ob.gif'::character varying,
    tablename character varying(128),
    namedinstances boolean DEFAULT true,
    isop boolean DEFAULT false,
    isvirtual boolean DEFAULT false,
    isdynamic boolean DEFAULT false,
    owner character varying(128) DEFAULT 'core'::character varying,
    obtypedescription character varying(2048)
);


ALTER TABLE public.obtype OWNER TO agrbrdf;

--
-- Name: TABLE obtype; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON TABLE obtype IS 'Types of object and relation stored in the brdf schema ';


--
-- Name: COLUMN obtype.tablename; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN obtype.tablename IS 'Unary relations are called facts, stored in tables named *fact ; binary relations are called links, 
stored in tables named *link ; ternary and higher relations are called either functions or studies and are stored in tables called
*function, or *study ';


--
-- Name: COLUMN obtype.namedinstances; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN obtype.namedinstances IS 'Most objects and relations are stored in tables that inherit from the ob table, and hence 
each instance is assigned a unique numeric name (obid) - namedinstances is TRUE for these. Some relations are stored 
in tables that do not inherit from the ob table, and do not have obids - namedInstances is FALSE for these.';


--
-- Name: COLUMN obtype.isop; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN obtype.isop IS 'Database entities are either primary objects such as sequences,samples, genes (obs), or 
relations (operations, or ops) between primary objects - e.g. op1(ob1,ob2,ob3...). Obs and ops may also be interpreted 
as nodes and edges in a hypergraph. isop is TRUE for ops or FALSE for obs';


--
-- Name: COLUMN obtype.isvirtual; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN obtype.isvirtual IS 'In most cases there is one database table for each type. Some types share a table - these are 
virtual types. is virtual is FALSE for most types, TRUE for types that share a table with another primary type';


--
-- Name: COLUMN obtype.isdynamic; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN obtype.isdynamic IS 'In most cases there is one database table for each type. However some types are not stored in a 
database table  but are constructed dynamically at run time';


--
-- Name: obtype_obtypeidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE obtype_obtypeidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.obtype_obtypeidseq OWNER TO agrbrdf;

--
-- Name: obtypesignature; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE obtypesignature (
    obtypeid integer NOT NULL,
    mandatoryoptype integer
);


ALTER TABLE public.obtypesignature OWNER TO agrbrdf;

--
-- Name: ontologyfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE ontologyfact (
    ontologyob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.ontologyfact OWNER TO agrbrdf;

--
-- Name: ontologyob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE ontologyob (
    ontologyname character varying(256) NOT NULL,
    ontologydescription character varying(1024),
    ontologycomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 5))
)
INHERITS (ob);


ALTER TABLE public.ontologyob OWNER TO agrbrdf;

--
-- Name: ontologytermfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE ontologytermfact (
    ontologyob integer NOT NULL,
    termname character varying(256),
    termdescription character varying(2048),
    unitname character varying(256),
    termcode character varying(16),
    CONSTRAINT "$1" CHECK ((obtypeid = 10))
)
INHERITS (op);


ALTER TABLE public.ontologytermfact OWNER TO agrbrdf;

--
-- Name: ontologytermfact2; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE ontologytermfact2 (
    ontologytermid integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.ontologytermfact2 OWNER TO agrbrdf;

--
-- Name: optypesignature; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE optypesignature (
    obtypeid integer NOT NULL,
    argobtypeid integer NOT NULL,
    optablecolumn character varying(128)
);


ALTER TABLE public.optypesignature OWNER TO agrbrdf;

--
-- Name: oracle_microarray_experiment; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE oracle_microarray_experiment (
    experimentid integer,
    seriesid integer,
    slideid integer,
    experimentname character varying(64),
    shortdescr character varying(128),
    longdescr character varying(500),
    resultsdatafilename character varying(1024),
    resultsdatafiletype character varying(32),
    resultsdatafiledate character varying(32),
    scansettingsfile character varying(1024),
    spottrackingfileused character varying(1024),
    scancomment character varying(128),
    scantool character varying(64),
    pixelsize integer,
    nputimagefilenames character varying(1024),
    outputimagefilenames character varying(1024),
    nf_ratioofmedians double precision,
    nf_ratioofmeans double precision,
    nf_medianofratios double precision,
    nf_meanofratios double precision,
    nf_regressionratio double precision,
    ratioformulation character varying(32),
    inputimageorigin character varying(16),
    outputimageorigin character varying(16),
    experimentrundate character varying(32),
    datasubmitteddate character varying(32),
    datasubmittedby character varying(64),
    checksum double precision,
    checksumtype character varying(32),
    cy5sampledescr character varying(64),
    cy5tissuedescr character varying(64),
    cy5treatmentdescr character varying(64),
    cy3sampledescr character varying(64),
    cy3tissuedescr character varying(64),
    cy3treatmentdescr character varying(64),
    normalisationfactors character varying(256),
    focusposition double precision,
    linesaveraged double precision,
    pmtgain character varying(128),
    scanpower character varying(128),
    scanregion character varying(128),
    supplier character varying(256),
    backgroundsubtraction character varying(128),
    wavelengths character varying(128),
    normalisationmethod character varying(256),
    scanner character varying(256),
    featuretype character varying(64),
    temperature double precision,
    laserpower character varying(64),
    filters character varying(128),
    rescantype character varying(64),
    testcol double precision,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.oracle_microarray_experiment OWNER TO agrbrdf;

--
-- Name: oracle_seqsource; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE oracle_seqsource (
    sourcecode character varying(40),
    organismname character varying(40),
    animalname character varying(90),
    sex character varying(10),
    organ character varying(70),
    tissue character varying(290),
    age character varying(100),
    primerdna integer,
    primerpcr integer,
    description character varying(500),
    altlibnum integer,
    organismcode character varying(20),
    breed character varying(50),
    strategydescription character varying(90),
    taxonid integer,
    genotype character varying(10),
    phenotype integer,
    kingdom character varying(10),
    secondspeciestaxid integer,
    strain integer,
    cultivar character varying(10),
    variety integer,
    sequencetype character varying(10),
    sequencesubtype character varying(10),
    expectedsize integer,
    access_flag integer,
    projectid integer,
    preparation_protocol character varying(130),
    fvector_name character varying(20),
    fvector_dbxref integer,
    rvector_name character varying(20),
    rvector_dbxref integer,
    libprepdate character varying(30),
    libpreparedby character varying(20),
    datasubmittedby character varying(10),
    growth_culture_age integer,
    growth_medium integer,
    growth_conditions integer,
    vector_supplier character varying(20),
    restriction_enzymes character varying(10),
    inserts_size character varying(20),
    host_strain character varying(10),
    amplified integer,
    labbook_owner character varying(20),
    labbook_ref character varying(30),
    labbook_pages character varying(10),
    projectcodeid integer,
    seqdbid integer,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.oracle_seqsource OWNER TO agrbrdf;

--
-- Name: pedigreelink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE pedigreelink (
    subjectob integer NOT NULL,
    objectob integer NOT NULL,
    relationship character varying(64),
    relationshipcomment character varying(256),
    CONSTRAINT "$1" CHECK ((obtypeid = 335))
)
INHERITS (op);


ALTER TABLE public.pedigreelink OWNER TO agrbrdf;

--
-- Name: phenotypeobservation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE phenotypeobservation (
    biosampleob integer,
    biosamplelist integer,
    biosubjectob integer,
    phenotypestudy integer NOT NULL,
    phenotypenamespace character varying(1024),
    phenotypeterm character varying(2048),
    phenotyperawscore double precision,
    phenotypeadjustedscore double precision,
    observationcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 155))
)
INHERITS (op);


ALTER TABLE public.phenotypeobservation OWNER TO agrbrdf;

--
-- Name: phenotypestudy; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE phenotypestudy (
    studyname character varying(1024) NOT NULL,
    phenotypeontologyname character varying(256) DEFAULT 'MYPHENOTYPE'::character varying,
    studydescription text,
    studydate date,
    CONSTRAINT "$1" CHECK ((obtypeid = 150))
)
INHERITS (ob);


ALTER TABLE public.phenotypestudy OWNER TO agrbrdf;

--
-- Name: platypusorthologs; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE platypusorthologs (
    orthogene character varying(2048),
    wallabyortholog integer,
    platypusortholog integer,
    humanplacentalortholog integer,
    cattleplacentalortholog integer
);


ALTER TABLE public.platypusorthologs OWNER TO agrbrdf;

--
-- Name: possumjunk1; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE possumjunk1 (
    besthit character varying(64),
    tax_id integer,
    geneid character varying(32),
    symbol character varying(64),
    locustag character varying(64),
    synonyms character varying(2048),
    chromosome character varying(64),
    map_location character varying(64),
    description character varying(256),
    type_of_gene character varying(64)
);


ALTER TABLE public.possumjunk1 OWNER TO agrbrdf;

--
-- Name: possumjunk3; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE possumjunk3 (
    geneid character varying(32),
    symbol character varying(32),
    accession character varying(32),
    description character varying(64),
    tax_id integer
);


ALTER TABLE public.possumjunk3 OWNER TO agrbrdf;

--
-- Name: predicatelink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE predicatelink (
    subjectob integer NOT NULL,
    objectob integer NOT NULL,
    predicate character varying(64),
    predicatecomment character varying(256),
    CONSTRAINT "$1" CHECK ((obtypeid = 15))
)
INHERITS (op);


ALTER TABLE public.predicatelink OWNER TO agrbrdf;

--
-- Name: predicatelinkfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE predicatelinkfact (
    predicatelink integer NOT NULL,
    factnamespace character varying(256),
    attributedate date,
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.predicatelinkfact OWNER TO agrbrdf;

--
-- Name: print139annotation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE print139annotation (
    contentid character varying(128),
    estname character varying(128),
    contig character varying(128),
    libexpression character varying(5192),
    hs_mm_rn_nr_gene character varying(32),
    taxid character varying(32),
    symbol character varying(256),
    synonyms character varying(256),
    chromosome character varying(128),
    map_location character varying(64),
    description character varying(5192),
    type_of_gene character varying(64),
    dummy character varying(4),
    datasourceob integer,
    voptypeid integer,
    symbolaccession character varying(64),
    oarchromosome character varying(32)
);


ALTER TABLE public.print139annotation OWNER TO agrbrdf;

--
-- Name: print139annotation_v1; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE print139annotation_v1 (
    arraygene_name character varying(20),
    estname character varying(30),
    spotlsid character varying(40),
    contig character varying(30),
    tissue_expression character varying(260),
    humanovermouseoverrat_gene_id character varying(10),
    gene_taxid character varying(10),
    gene_symbol character varying(30),
    symbol_accession_for_ingenuity character varying(50),
    synonyms character varying(130),
    accession_chromosome character varying(20),
    map_location character varying(40),
    gene_description character varying(260),
    type_of_gene character varying(20),
    eof integer,
    datasourceob integer,
    voptypeid integer,
    oarchromosome character varying(32),
    contentid character varying(128)
);


ALTER TABLE public.print139annotation_v1 OWNER TO agrbrdf;

--
-- Name: print139annotationbackup; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE print139annotationbackup (
    contentid character varying(128),
    estname character varying(128),
    contig character varying(128),
    libexpression character varying(5192),
    hs_mm_rn_nr_gene character varying(32),
    taxid character varying(32),
    symbol character varying(256),
    synonyms character varying(256),
    chromosome character varying(128),
    map_location character varying(64),
    description character varying(5192),
    type_of_gene character varying(64),
    dummy character varying(4),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.print139annotationbackup OWNER TO agrbrdf;

--
-- Name: print139annotationbackup2; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE print139annotationbackup2 (
    contentid character varying(128),
    estname character varying(128),
    contig character varying(128),
    libexpression character varying(5192),
    hs_mm_rn_nr_gene character varying(32),
    taxid character varying(32),
    symbol character varying(256),
    synonyms character varying(256),
    chromosome character varying(128),
    map_location character varying(64),
    description character varying(5192),
    type_of_gene character varying(64),
    dummy character varying(4),
    datasourceob integer,
    voptypeid integer,
    symbolaccession character varying(64),
    oarchromosome character varying(32)
);


ALTER TABLE public.print139annotationbackup2 OWNER TO agrbrdf;

--
-- Name: reproductionmicroarrayplasmids; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE reproductionmicroarrayplasmids (
    microarray_code character varying(10),
    plasmid_id character varying(10),
    vector_id character varying(20),
    species character varying(10),
    gene character varying(20),
    geneid character varying(10),
    gene_name character varying(80),
    size_bp character varying(10),
    primer_pairs character varying(10),
    dna_concentration character varying(20),
    conc_in_ngoverul character varying(20),
    dilute_by_to_get_50_ngoverul character varying(10),
    sample_ul character varying(10),
    water_ul character varying(10),
    col character varying(10),
    col_1 integer,
    microarray_code_1 character varying(10),
    plasmid_id_1 character varying(10),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.reproductionmicroarrayplasmids OWNER TO agrbrdf;

--
-- Name: samplesheet_temp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE samplesheet_temp (
    fcid character varying(32),
    lane integer,
    sampleid character varying(32),
    sampleref character varying(32),
    sampleindex character varying(1024),
    description character varying(256),
    control character varying(32),
    recipe integer,
    operator character varying(256),
    sampleproject character varying(256),
    sampleplate character varying(64),
    samplewell character varying(64),
    downstream_processing character varying(64),
    basespace_project character varying(256)
);


ALTER TABLE public.samplesheet_temp OWNER TO agrbrdf;

--
-- Name: scratch; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE scratch (
    xreflsid character varying(128)
);


ALTER TABLE public.scratch OWNER TO agrbrdf;

--
-- Name: securityfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE securityfunction (
    ob integer,
    applytotype integer,
    securityprocedureob integer NOT NULL,
    functioncomment character varying(1024),
    invocation text,
    invocationorder integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 465))
)
INHERITS (op);


ALTER TABLE public.securityfunction OWNER TO agrbrdf;

--
-- Name: securityprocedureob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE securityprocedureob (
    procedurename character varying(1024),
    author character varying(2048),
    authordate date,
    sourcecode text,
    proceduredescription character varying(1024),
    procedurecomment text,
    invocation text,
    CONSTRAINT "$1" CHECK ((obtypeid = 460))
)
INHERITS (ob);


ALTER TABLE public.securityprocedureob OWNER TO agrbrdf;

--
-- Name: sequencealignmentfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE sequencealignmentfact (
    databasesearchobservation integer NOT NULL,
    bitscore double precision,
    score double precision,
    evalue double precision,
    queryfrom numeric(12,0),
    queryto numeric(12,0),
    hitfrom numeric(12,0),
    hitto numeric(12,0),
    queryframe integer,
    hitframe integer,
    identities integer,
    positives integer,
    alignlen integer,
    hspqseq text,
    hsphseq text,
    hspmidline text,
    alignmentcomment character varying(2048),
    hitstrand integer,
    gaps integer,
    mismatches integer,
    pctidentity double precision,
    indels integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 330))
)
INHERITS (op);


ALTER TABLE public.sequencealignmentfact OWNER TO agrbrdf;

--
-- Name: sequencingfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE sequencingfact (
    sequencingfunction integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.sequencingfact OWNER TO agrbrdf;

--
-- Name: sequencingfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE sequencingfunction (
    biosampleob integer,
    biosequenceob integer NOT NULL,
    labresourcelist integer,
    labresourceob integer,
    sequencedby character varying(256),
    sequencingdate date,
    functioncomment character varying(1024),
    biolibraryob integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 120))
)
INHERITS (op);


ALTER TABLE public.sequencingfunction OWNER TO agrbrdf;

--
-- Name: sheepv3_prot_annotation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE sheepv3_prot_annotation (
    seqid character varying(20),
    source character varying(10),
    type character varying(10),
    start integer,
    stop integer,
    score character varying(10),
    strand character varying(10),
    phase character varying(10),
    gene_model character varying(120),
    interproscan character varying(100),
    interproscan_go character varying(210),
    kegg character varying(470),
    swissprot character varying(160),
    datasourceob integer,
    voptypeid integer,
    seqname character varying(50)
);


ALTER TABLE public.sheepv3_prot_annotation OWNER TO agrbrdf;

--
-- Name: spotidmapcaco2; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE spotidmapcaco2 (
    gal_refnumber integer,
    microarrayspotfact integer,
    recnum integer,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.spotidmapcaco2 OWNER TO agrbrdf;

--
-- Name: stafffact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE stafffact (
    staffob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.stafffact OWNER TO agrbrdf;

--
-- Name: staffob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE staffob (
    loginname character varying(64) NOT NULL,
    fullname character varying(128),
    emailaddress character varying(256),
    mobile character varying(64),
    phone character varying(64),
    title character varying(32),
    staffcomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 50))
)
INHERITS (ob);


ALTER TABLE public.staffob OWNER TO agrbrdf;

--
-- Name: t_animal_fact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE t_animal_fact (
    animalid integer,
    labid character varying(20),
    stud character varying(20),
    yob integer,
    uidtag character varying(60),
    sex character varying(10),
    species character varying(20),
    damid integer,
    sireid integer,
    ownerid integer,
    breed character varying(40),
    family character varying(10),
    sil_ignore character varying(10),
    sil_reconciled character varying(10),
    sil_requery character varying(10),
    sil_sex character varying(20),
    sil_status character varying(20),
    comment character varying(230),
    birthdate character varying(20),
    sys_created character varying(30),
    sys_createdby character varying(20),
    ovitacontractnumber character varying(40),
    sil_tag character varying(20),
    sil_flock_code integer,
    sil_reconciled_date character varying(30),
    biosubjectob integer NOT NULL
);


ALTER TABLE public.t_animal_fact OWNER TO agrbrdf;

--
-- Name: t_sample_fact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE t_sample_fact (
    labid character varying(20),
    sampleid character varying(40),
    sample_type character varying(20),
    animalid integer,
    mixid integer,
    ownerid integer,
    date_received character varying(20),
    restricted_use character varying(10),
    sys_created character varying(20),
    sys_createdby character varying(20),
    max_kgd_sampdepth double precision,
    biosubjectob integer
);


ALTER TABLE public.t_sample_fact OWNER TO agrbrdf;

--
-- Name: taxonomy_names; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE taxonomy_names (
    tax_id integer,
    name_txt character varying(1024),
    unique_name character varying(1024),
    name_class character varying(1024),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.taxonomy_names OWNER TO agrbrdf;

--
-- Name: urilink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE urilink (
    uriob integer NOT NULL,
    ob integer NOT NULL,
    displaystring character varying(2048),
    displayorder integer,
    iconpath character varying(512),
    iconattributes character varying(2048),
    createddate date DEFAULT now(),
    createdby character varying(256),
    lastupdateddate date,
    lastupdatedby character varying(256),
    uricomment character varying(256),
    linktype character varying(256)
);


ALTER TABLE public.urilink OWNER TO agrbrdf;

--
-- Name: uriob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE uriob (
    uristring character varying(2048) NOT NULL,
    uritype character varying(256),
    uricomment character varying(1024),
    visibility character varying(32) DEFAULT 'public'::character varying,
    CONSTRAINT "$1" CHECK ((obtypeid = 30))
)
INHERITS (ob);


ALTER TABLE public.uriob OWNER TO agrbrdf;

--
-- Name: wheatchipannotation2011; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE wheatchipannotation2011 (
    probeset character varying(30),
    log_ratio double precision,
    fold_change double precision,
    biological_fold_change double precision,
    absolute_biol_fold_change double precision,
    monad_3060_geomean integer,
    monad_e__geomean integer,
    maximum_geomean integer,
    moderated_p_value double precision,
    fdr double precision,
    logmod_p double precision,
    logfdr double precision,
    monad_3060_flag integer,
    monad_e__flag integer,
    mg0001_wheat_cel character varying(10),
    mg0003_wheat_cel character varying(10),
    mg0004_wheat_cel character varying(10),
    mg0005_wheat_cel character varying(10),
    mg0006_wheat_cel character varying(10),
    mg0007_wheat_cel character varying(10),
    monad_3060_pma_calls character varying(10),
    monad_e__pma_calls character varying(10),
    log_ratio_1 double precision,
    fold_change_1 double precision,
    biological_fold_change_1 double precision,
    absolute_biol_fold_change_1 double precision,
    monad_3060_geomean_1 integer,
    monad_e__geomean_1 integer,
    maximum_geomean_1 integer,
    moderated_p_value_1 double precision,
    fdr_1 double precision,
    logmod_p_1 double precision,
    logfdr_1 double precision,
    sequence_source character varying(40),
    transcript_idarray_design character varying(20),
    target_description character varying(550),
    representative_public_id character varying(30),
    representative_public_id_1 character varying(30),
    archival_unigene_cluster character varying(10),
    unigene_id character varying(50),
    unigene_id_1 character varying(50),
    genome_version character varying(10),
    alignments character varying(10),
    gene_title character varying(250),
    gene_symbol character varying(100),
    chromosomal_location character varying(10),
    unigene_cluster_type character varying(20),
    ensembl character varying(10),
    entrez_gene character varying(80),
    entrez_gene_1 character varying(80),
    swissprot character varying(390),
    gene_ontology_biological_process character varying(1300),
    gene_ontology_cellular_component character varying(630),
    gene_ontology_molecular_function character varying(1950),
    interpro character varying(350),
    trans_membrane character varying(760),
    annotation_description character varying(190),
    annotation_transcript_cluster character varying(4140),
    transcript_assignments character varying(29950),
    annotation_notes character varying(15990),
    uniref90_hit_accession__harvest_11over2010 character varying(100),
    uniref90_hit_accession__harvest_11over2010_1 character varying(100),
    uniref90_hit_description__harvest_11over2010 character varying(170),
    uniref90_e_value__harvest_11over2010 character varying(120),
    go_molecular_function_ids__agrigo_11over2010 character varying(160),
    go_molecular_function_terms__agrigo_11over2010 character varying(400),
    go_biological_process_ids__agrigo_11over2010 character varying(460),
    go_biological_process_terms__agrigo_11over2010 character varying(1190),
    go_cellular_component_ids__agrigo_11over2010 character varying(120),
    go_cellular_component_terms__agrigo_11over2010 character varying(200),
    go_missing_info_ids__agrigo_11over2010 character varying(30),
    go_missing_info_terms__agrigo_11over2010 character varying(40),
    probeid character varying(30),
    probe_set_name_found character varying(30),
    exemplar_assembly character varying(10),
    exemplar_unigene character varying(20),
    pre_polya_trim_length integer,
    members integer,
    num__unigenes integer,
    unigenes_represented character varying(910),
    uniprot_accn character varying(30),
    uniprot_e_score double precision,
    uniprot_desc character varying(170),
    rice_accn character varying(20),
    rice_e_score double precision,
    rice_chr integer,
    rice_5prime integer,
    rice_3prime integer,
    rice_desc character varying(130),
    arab_accn character varying(20),
    arab_e_score double precision,
    arab_chr character varying(10),
    arab_5prime integer,
    arab_3prime integer,
    arab_desc character varying(140),
    brachy_accn character varying(20),
    brachy_e_score double precision,
    brachy_chr character varying(10),
    brachy_5primepluscu3 integer,
    brachy_3prime integer,
    brachy_desc character varying(90),
    eof integer,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.wheatchipannotation2011 OWNER TO agrbrdf;

--
-- Name: wheatrma; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE wheatrma (
    gene character varying(30),
    uninfected_1 double precision,
    uninfected_2 double precision,
    uninfected_3 double precision,
    infected_1 double precision,
    infected_2 double precision,
    infected_3 double precision,
    datasourceob integer,
    voptypeid integer,
    fileorder integer
);


ALTER TABLE public.wheatrma OWNER TO agrbrdf;

--
-- Name: workflowlink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE workflowlink (
    fromstage integer NOT NULL,
    tostage integer NOT NULL,
    workcomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 220))
)
INHERITS (op);


ALTER TABLE public.workflowlink OWNER TO agrbrdf;

--
-- Name: workflowmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE workflowmembershiplink (
    workflowob integer NOT NULL,
    workflowstageob integer NOT NULL,
    membershipcomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 215))
)
INHERITS (op);


ALTER TABLE public.workflowmembershiplink OWNER TO agrbrdf;

--
-- Name: workflowob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE workflowob (
    workflowname character varying(256),
    workflowdescription character varying(2048),
    workflowcomment text,
    CONSTRAINT workflowob_workflowcomment CHECK ((obtypeid = 205))
)
INHERITS (ob);


ALTER TABLE public.workflowob OWNER TO agrbrdf;

--
-- Name: workflowstageob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE workflowstageob (
    workflowstagename character varying(256),
    workflowstagetype character varying(64),
    workflowstagedescription character varying(2048),
    workflowstagecomment text,
    CONSTRAINT workflowstageob_workflowstagecomment CHECK ((obtypeid = 210))
)
INHERITS (ob);


ALTER TABLE public.workflowstageob OWNER TO agrbrdf;

--
-- Name: working_temp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE working_temp (
    biosamplelist integer,
    biosampleob integer,
    inclusioncomment character varying(64),
    addeddate date,
    addedby character varying(256)
);


ALTER TABLE public.working_temp OWNER TO agrbrdf;

--
-- Name: workstagevisitfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE workstagevisitfact (
    workflowstage integer NOT NULL,
    workdoneby character varying(256),
    workdonedate date,
    workcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 225))
)
INHERITS (op);


ALTER TABLE public.workstagevisitfact OWNER TO agrbrdf;

--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisprocedureob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisprocedureob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisprocedureob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisprocedureob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisprocedureob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biodatabaseob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biodatabaseob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biodatabaseob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biodatabaseob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biodatabaseob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY bioprotocolob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY bioprotocolob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY bioprotocolob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY bioprotocolob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY bioprotocolob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplealiquotfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplealiquotfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplealiquotfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplealiquotfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplealiquotfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplelist ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplelist ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplelist ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplelist ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplelist ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosampleob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosampleob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosampleob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosampleob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosampleob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequenceob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequenceob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequenceob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequenceob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequenceob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY commentob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY commentob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY commentob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY commentob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY commentob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchstudy ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchstudy ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchstudy ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchstudy ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchstudy ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourcelist ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourcelist ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourcelist ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourcelist ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourcelist ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourceob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourceob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourceob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourceob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourceob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayprocedureob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayprocedureob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayprocedureob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayprocedureob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayprocedureob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneexpressionstudy ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneexpressionstudy ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneexpressionstudy ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneexpressionstudy ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneexpressionstudy ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneproductlink ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneproductlink ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneproductlink ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneproductlink ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneproductlink ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY generegulationlink ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY generegulationlink ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY generegulationlink ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY generegulationlink ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY generegulationlink ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfunctionfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfunctionfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfunctionfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfunctionfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfunctionfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationlist ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationlist ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationlist ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationlist ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationlist ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticoblist ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticoblist ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticoblist ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticoblist ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticoblist ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genetictestfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genetictestfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genetictestfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genetictestfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genetictestfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypeobservation ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypeobservation ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypeobservation ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypeobservation ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypeobservation ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importprocedureob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importprocedureob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importprocedureob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importprocedureob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importprocedureob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourcelist ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourcelist ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourcelist ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourcelist ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourcelist ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourceob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourceob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourceob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourceob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourceob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY literaturereferenceob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY literaturereferenceob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY literaturereferenceob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY literaturereferenceob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY literaturereferenceob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayobservation ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayobservation ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayobservation ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayobservation ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayobservation ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayspotfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayspotfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayspotfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayspotfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayspotfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY oblist ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY oblist ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY oblist ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY oblist ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY oblist ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologyob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologyob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologyob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologyob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologyob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologytermfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologytermfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologytermfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologytermfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologytermfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY op ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY op ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY op ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY op ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY op ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY pedigreelink ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY pedigreelink ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY pedigreelink ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY pedigreelink ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY pedigreelink ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypestudy ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypestudy ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypestudy ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypestudy ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypestudy ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY predicatelink ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY predicatelink ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY predicatelink ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY predicatelink ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY predicatelink ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityprocedureob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityprocedureob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityprocedureob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityprocedureob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityprocedureob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencealignmentfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencealignmentfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencealignmentfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencealignmentfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencealignmentfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY staffob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY staffob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY staffob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY staffob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY staffob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY uriob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY uriob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY uriob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY uriob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY uriob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowlink ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowlink ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowlink ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowlink ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowlink ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowmembershiplink ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowmembershiplink ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowmembershiplink ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowmembershiplink ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowmembershiplink ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowstageob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowstageob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowstageob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowstageob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowstageob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: analysisfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY analysisfunction
    ADD CONSTRAINT analysisfunction_obid_key UNIQUE (obid);


--
-- Name: analysisprocedureob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY analysisprocedureob
    ADD CONSTRAINT analysisprocedureob_obid_key UNIQUE (obid);


--
-- Name: biodatabaseob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biodatabaseob
    ADD CONSTRAINT biodatabaseob_obid_key UNIQUE (obid);


--
-- Name: biolibraryconstructionfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_obid_key UNIQUE (obid);


--
-- Name: biolibraryob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biolibraryob
    ADD CONSTRAINT biolibraryob_obid_key UNIQUE (obid);


--
-- Name: bioprotocolob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY bioprotocolob
    ADD CONSTRAINT bioprotocolob_obid_key UNIQUE (obid);


--
-- Name: biosamplealiquotfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biosamplealiquotfact
    ADD CONSTRAINT biosamplealiquotfact_obid_key UNIQUE (obid);


--
-- Name: biosamplelist_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biosamplelist
    ADD CONSTRAINT biosamplelist_obid_key UNIQUE (obid);


--
-- Name: biosampleob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biosampleob
    ADD CONSTRAINT biosampleob_obid_key UNIQUE (obid);


--
-- Name: biosamplingfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT biosamplingfunction_obid_key UNIQUE (obid);


--
-- Name: biosequencefeaturefact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biosequencefeaturefact
    ADD CONSTRAINT biosequencefeaturefact_obid_key UNIQUE (obid);


--
-- Name: biosequenceob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biosequenceob
    ADD CONSTRAINT biosequenceob_obid_key UNIQUE (obid);


--
-- Name: biosubjectob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biosubjectob
    ADD CONSTRAINT biosubjectob_obid_key UNIQUE (obid);


--
-- Name: commentob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY commentob
    ADD CONSTRAINT commentob_obid_key UNIQUE (obid);


--
-- Name: databasesearchobservation_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY databasesearchobservation
    ADD CONSTRAINT databasesearchobservation_obid_key UNIQUE (obid);


--
-- Name: databasesearchstudy_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY databasesearchstudy
    ADD CONSTRAINT databasesearchstudy_obid_key UNIQUE (obid);


--
-- Name: datasourcelist_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY datasourcelist
    ADD CONSTRAINT datasourcelist_obid_key UNIQUE (obid);


--
-- Name: datasourceob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY datasourceob
    ADD CONSTRAINT datasourceob_obid_key UNIQUE (obid);


--
-- Name: displayfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY displayfunction
    ADD CONSTRAINT displayfunction_obid_key UNIQUE (obid);


--
-- Name: displayprocedureob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY displayprocedureob
    ADD CONSTRAINT displayprocedureob_obid_key UNIQUE (obid);


--
-- Name: gbskeyfilefact_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY gbskeyfilefact
    ADD CONSTRAINT gbskeyfilefact_pkey PRIMARY KEY (factid);


--
-- Name: gbsyieldfact_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY gbsyieldfact
    ADD CONSTRAINT gbsyieldfact_pkey PRIMARY KEY (factid);


--
-- Name: geneexpressionstudy_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY geneexpressionstudy
    ADD CONSTRAINT geneexpressionstudy_obid_key UNIQUE (obid);


--
-- Name: geneticexpressionfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY geneticexpressionfact
    ADD CONSTRAINT geneticexpressionfact_obid_key UNIQUE (obid);


--
-- Name: geneticlocationfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY geneticlocationfact
    ADD CONSTRAINT geneticlocationfact_obid_key UNIQUE (obid);


--
-- Name: geneticlocationlist_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY geneticlocationlist
    ADD CONSTRAINT geneticlocationlist_obid_key UNIQUE (obid);


--
-- Name: geneticob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY geneticob
    ADD CONSTRAINT geneticob_obid_key UNIQUE (obid);


--
-- Name: geneticoblist_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY geneticoblist
    ADD CONSTRAINT geneticoblist_obid_key UNIQUE (obid);


--
-- Name: genetictestfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY genetictestfact
    ADD CONSTRAINT genetictestfact_obid_key UNIQUE (obid);


--
-- Name: genotypeobservation_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY genotypeobservation
    ADD CONSTRAINT genotypeobservation_obid_key UNIQUE (obid);


--
-- Name: genotypestudy_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT genotypestudy_obid_key UNIQUE (obid);


--
-- Name: hiseqsamplesheetfact_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY hiseqsamplesheetfact
    ADD CONSTRAINT hiseqsamplesheetfact_pkey PRIMARY KEY (factid);


--
-- Name: importfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY importfunction
    ADD CONSTRAINT importfunction_obid_key UNIQUE (obid);


--
-- Name: importprocedureob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY importprocedureob
    ADD CONSTRAINT importprocedureob_obid_key UNIQUE (obid);


--
-- Name: labresourcelist_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY labresourcelist
    ADD CONSTRAINT labresourcelist_obid_key UNIQUE (obid);


--
-- Name: labresourceob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY labresourceob
    ADD CONSTRAINT labresourceob_obid_key UNIQUE (obid);


--
-- Name: librarysequencingfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_obid_key UNIQUE (obid);


--
-- Name: listmembershipfact_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY listmembershipfact
    ADD CONSTRAINT listmembershipfact_pkey PRIMARY KEY (factid);


--
-- Name: literaturereferenceob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY literaturereferenceob
    ADD CONSTRAINT literaturereferenceob_obid_key UNIQUE (obid);


--
-- Name: microarrayfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY microarrayfact
    ADD CONSTRAINT microarrayfact_obid_key UNIQUE (obid);


--
-- Name: microarrayobservation_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY microarrayobservation
    ADD CONSTRAINT microarrayobservation_obid_key UNIQUE (obid);


--
-- Name: microarrayspotfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY microarrayspotfact
    ADD CONSTRAINT microarrayspotfact_obid_key UNIQUE (obid);


--
-- Name: ob_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY ob
    ADD CONSTRAINT ob_pkey PRIMARY KEY (obid);


--
-- Name: oblist_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY oblist
    ADD CONSTRAINT oblist_obid_key UNIQUE (obid);


--
-- Name: obstatus_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY obstatus
    ADD CONSTRAINT obstatus_pkey PRIMARY KEY (statuscode);


--
-- Name: obtype_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY obtype
    ADD CONSTRAINT obtype_pkey PRIMARY KEY (obtypeid);


--
-- Name: ontologyob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY ontologyob
    ADD CONSTRAINT ontologyob_obid_key UNIQUE (obid);


--
-- Name: ontologytermfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY ontologytermfact
    ADD CONSTRAINT ontologytermfact_obid_key UNIQUE (obid);


--
-- Name: pedigreelink_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY pedigreelink
    ADD CONSTRAINT pedigreelink_obid_key UNIQUE (obid);


--
-- Name: phenotypeobservation_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY phenotypeobservation
    ADD CONSTRAINT phenotypeobservation_obid_key UNIQUE (obid);


--
-- Name: phenotypestudy_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY phenotypestudy
    ADD CONSTRAINT phenotypestudy_obid_key UNIQUE (obid);


--
-- Name: predicatelink_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY predicatelink
    ADD CONSTRAINT predicatelink_obid_key UNIQUE (obid);


--
-- Name: securityfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY securityfunction
    ADD CONSTRAINT securityfunction_obid_key UNIQUE (obid);


--
-- Name: securityprocedureob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY securityprocedureob
    ADD CONSTRAINT securityprocedureob_obid_key UNIQUE (obid);


--
-- Name: sequencealignmentfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY sequencealignmentfact
    ADD CONSTRAINT sequencealignmentfact_obid_key UNIQUE (obid);


--
-- Name: sequencingfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT sequencingfunction_obid_key UNIQUE (obid);


--
-- Name: staffob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY staffob
    ADD CONSTRAINT staffob_obid_key UNIQUE (obid);


--
-- Name: uriob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY uriob
    ADD CONSTRAINT uriob_obid_key UNIQUE (obid);


--
-- Name: workflowlink_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY workflowlink
    ADD CONSTRAINT workflowlink_obid_key UNIQUE (obid);


--
-- Name: workflowmembershiplink_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY workflowmembershiplink
    ADD CONSTRAINT workflowmembershiplink_obid_key UNIQUE (obid);


--
-- Name: workflowob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY workflowob
    ADD CONSTRAINT workflowob_obid_key UNIQUE (obid);


--
-- Name: workflowstageob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY workflowstageob
    ADD CONSTRAINT workflowstageob_obid_key UNIQUE (obid);


--
-- Name: workstagevisitfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY workstagevisitfact
    ADD CONSTRAINT workstagevisitfact_obid_key UNIQUE (obid);


--
-- Name: anneoconnelprobenames_prop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX anneoconnelprobenames_prop ON anneoconnelprobenames USING btree (propname);


--
-- Name: blastn_results_queryid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX blastn_results_queryid ON blastn_results USING btree (queryid);


--
-- Name: blastn_results_queryidevalue; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX blastn_results_queryidevalue ON blastn_results USING btree (queryid, evalue);


--
-- Name: blastn_results_queryidevaluescore; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX blastn_results_queryidevaluescore ON blastn_results USING btree (queryid, evalue, score);


--
-- Name: blastx_results_queryid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX blastx_results_queryid ON blastx_results USING btree (queryid);


--
-- Name: blastx_results_queryidevalue; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX blastx_results_queryidevalue ON blastx_results USING btree (queryid, evalue);


--
-- Name: geo_gene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX geo_gene ON geosubmissiondata USING btree (gene_name);


--
-- Name: geo_id_ref; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX geo_id_ref ON geosubmissiondata USING btree (id_ref);


--
-- Name: geo_symbol; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX geo_symbol ON geosubmissiondata USING btree (genesymbol);


--
-- Name: hg18_cpg_chromstart; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_cpg_chromstart ON hg18_cpg_location USING btree (chrom, chromstart);


--
-- Name: hg18_cpg_chromstartstop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_cpg_chromstartstop ON hg18_cpg_location USING btree (chrom, chromstart, chromend);


--
-- Name: hg18_mspi_chromstart; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_mspi_chromstart ON hg18_mspi_digest USING btree (chrom, start);


--
-- Name: hg18_mspi_chromstartstop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_mspi_chromstartstop ON hg18_mspi_digest USING btree (chrom, start, stop);


--
-- Name: hg18_refgenes_cdsstart; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_refgenes_cdsstart ON hg18_refgenes_location USING btree (chrom, cdsstart);


--
-- Name: hg18_refgenes_cdsstartstop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_refgenes_cdsstartstop ON hg18_refgenes_location USING btree (chrom, cdsstart, cdsend);


--
-- Name: hg18_refgenes_transstart; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_refgenes_transstart ON hg18_refgenes_location USING btree (chrom, transcriptionstart, strand);


--
-- Name: hg18_refgenes_transstartstop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_refgenes_transstartstop ON hg18_refgenes_location USING btree (chrom, transcriptionstart, transcriptionend);


--
-- Name: hg18_refgenes_transstop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_refgenes_transstop ON hg18_refgenes_location USING btree (chrom, transcriptionend, strand);


--
-- Name: i_analysisfunction1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_analysisfunction1 ON analysisfunction USING btree (ob, voptypeid);


--
-- Name: i_bioprotocoloblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_bioprotocoloblsid ON bioprotocolob USING btree (xreflsid);


--
-- Name: i_biosamplefact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosamplefact1 ON biosamplefact USING btree (biosampleob);


--
-- Name: i_biosamplefact2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosamplefact2 ON biosamplefact USING btree (biosampleob, factnamespace, attributename);


--
-- Name: i_biosamplingfunctionlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosamplingfunctionlsid ON biosamplingfunction USING btree (xreflsid);


--
-- Name: i_biosamplingfunctionsample; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosamplingfunctionsample ON biosamplingfunction USING btree (biosampleob);


--
-- Name: i_biosamplingfunctionsubject; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosamplingfunctionsubject ON biosamplingfunction USING btree (biosubjectob);


--
-- Name: i_biosequencefact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequencefact1 ON biosequencefact USING btree (biosequenceob, factnamespace, attributename);


--
-- Name: i_biosequencefeatfact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequencefeatfact1 ON biosequencefeaturefact USING btree (biosequenceob);


--
-- Name: i_biosequencefeatfactacc; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequencefeatfactacc ON biosequencefeaturefact USING btree (featureaccession);


--
-- Name: i_biosequencefeaturefactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequencefeaturefactlsid ON biosequencefeaturefact USING btree (xreflsid);


--
-- Name: i_biosequenceobkw; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequenceobkw ON biosequenceob USING btree (obkeywords);


--
-- Name: i_biosequenceoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequenceoblsid ON biosequenceob USING btree (xreflsid);


--
-- Name: i_biosequenceobsn; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequenceobsn ON biosequenceob USING btree (sequencename);


--
-- Name: i_biosubjectfact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosubjectfact1 ON biosubjectfact USING btree (biosubjectob);


--
-- Name: i_biosubjectfact2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosubjectfact2 ON biosubjectfact USING btree (biosubjectob, factnamespace, attributename);


--
-- Name: i_bovine_est_entropies_estname; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_bovine_est_entropies_estname ON bovine_est_entropies USING btree (estname);


--
-- Name: i_commentlink; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_commentlink ON commentlink USING btree (ob, commentob);


--
-- Name: i_commentoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_commentoblsid ON commentob USING btree (xreflsid);


--
-- Name: i_datasourcefact; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_datasourcefact ON datasourcefact USING btree (datasourceob, factnamespace, attributename);


--
-- Name: i_datasourcename; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_datasourcename ON datasourceob USING btree (datasourcename);


--
-- Name: i_datasourceoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_datasourceoblsid ON datasourceob USING btree (xreflsid);


--
-- Name: i_dbsearchobservation_hit; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_hit ON databasesearchobservation USING btree (hitsequence);


--
-- Name: i_dbsearchobservation_lsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_lsid ON databasesearchobservation USING btree (xreflsid);


--
-- Name: i_dbsearchobservation_query; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_query ON databasesearchobservation USING btree (querysequence);


--
-- Name: i_dbsearchobservation_queryhit; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_queryhit ON databasesearchobservation USING btree (querysequence, hitsequence);


--
-- Name: i_dbsearchobservation_studyhit; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_studyhit ON databasesearchobservation USING btree (databasesearchstudy, hitsequence);


--
-- Name: i_dbsearchobservation_studyquery; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_studyquery ON databasesearchobservation USING btree (databasesearchstudy, querysequence);


--
-- Name: i_dbsearchobservation_studyqueryhit; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_studyqueryhit ON databasesearchobservation USING btree (databasesearchstudy, querysequence, hitsequence);


--
-- Name: i_displayfunctionds; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_displayfunctionds ON displayfunction USING btree (datasourceob);


--
-- Name: i_displayfunctionlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_displayfunctionlsid ON displayfunction USING btree (xreflsid);


--
-- Name: i_displayfunctionob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_displayfunctionob ON displayfunction USING btree (ob);


--
-- Name: i_displayfunctionobdp; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_displayfunctionobdp ON displayfunction USING btree (ob, displayprocedureob);


--
-- Name: i_displayprocedureoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_displayprocedureoblsid ON displayprocedureob USING btree (xreflsid);


--
-- Name: i_gbs_yield_import_temp_rss; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbs_yield_import_temp_rss ON gbs_yield_import_temp USING btree (run, sqname, sampleid);


--
-- Name: i_gbs_yield_import_temp_run; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbs_yield_import_temp_run ON gbs_yield_import_temp USING btree (run);


--
-- Name: i_gbs_yield_import_temp_samp; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbs_yield_import_temp_samp ON gbs_yield_import_temp USING btree (sampleid);


--
-- Name: i_gbs_yield_import_temp_sq; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbs_yield_import_temp_sq ON gbs_yield_import_temp USING btree (sqname);


--
-- Name: i_gbskeyfilefact_biosubject; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbskeyfilefact_biosubject ON gbskeyfilefact USING btree (biosubjectob);


--
-- Name: i_gbskeyfilefactsfl; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbskeyfilefactsfl ON gbskeyfilefact USING btree (sample, flowcell, lane);


--
-- Name: i_gbsyieldfactsamp; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbsyieldfactsamp ON gbsyieldfact USING btree (sampleid);


--
-- Name: i_gbsyieldfactsfl; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbsyieldfactsfl ON gbsyieldfact USING btree (sampleid, flowcell, lane);


--
-- Name: i_gbsyieldfactsq; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbsyieldfactsq ON gbsyieldfact USING btree (sqname);


--
-- Name: i_gbsyieldfactsqsamp; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbsyieldfactsqsamp ON gbsyieldfact USING btree (sqname, sampleid);


--
-- Name: i_gene2accession_geneid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gene2accession_geneid ON gene2accession USING btree (geneid);


--
-- Name: i_gene2accession_genomic; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gene2accession_genomic ON gene2accession USING btree (genomic_nucleotide_accession);


--
-- Name: i_gene2accession_nuc; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gene2accession_nuc ON gene2accession USING btree (rna_nucleotide_accession);


--
-- Name: i_gene2accession_prot; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gene2accession_prot ON gene2accession USING btree (protein_accession);


--
-- Name: i_gene2accession_taxid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gene2accession_taxid ON gene2accession USING btree (tax_id);


--
-- Name: i_geneexpressionstudylsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneexpressionstudylsid ON geneexpressionstudy USING btree (xreflsid);


--
-- Name: i_geneexpressionstudyname; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneexpressionstudyname ON geneexpressionstudy USING btree (studyname);


--
-- Name: i_geneproductlinkgene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneproductlinkgene ON geneproductlink USING btree (geneticob);


--
-- Name: i_geneproductlinklsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneproductlinklsid ON geneproductlink USING btree (xreflsid);


--
-- Name: i_geneproductlinkprod; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneproductlinkprod ON geneproductlink USING btree (biosequenceob);


--
-- Name: i_generegulationlinklsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_generegulationlinklsid ON generegulationlink USING btree (xreflsid);


--
-- Name: i_geneticexpress_bioseq; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticexpress_bioseq ON geneticexpressionfact USING btree (biosequenceob);


--
-- Name: i_geneticexpress_bioseqv; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticexpress_bioseqv ON geneticexpressionfact USING btree (biosequenceob, voptypeid);


--
-- Name: i_geneticexpress_gene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticexpress_gene ON geneticexpressionfact USING btree (geneticob);


--
-- Name: i_geneticexpressionfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticexpressionfactlsid ON geneticexpressionfact USING btree (xreflsid);


--
-- Name: i_geneticfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticfactlsid ON geneticfact USING btree (xreflsid);


--
-- Name: i_geneticfunctionfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticfunctionfactlsid ON geneticfunctionfact USING btree (xreflsid);


--
-- Name: i_geneticlocationfactgeneid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactgeneid ON geneticlocationfact USING btree (entrezgeneid);


--
-- Name: i_geneticlocationfactgeneticob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactgeneticob ON geneticlocationfact USING btree (geneticob);


--
-- Name: i_geneticlocationfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactlsid ON geneticlocationfact USING btree (xreflsid);


--
-- Name: i_geneticlocationfactmulti1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactmulti1 ON geneticlocationfact USING btree (entrezgeneid, evidence, geneticob);


--
-- Name: i_geneticlocationfactmulti2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactmulti2 ON geneticlocationfact USING btree (mapname, chromosomename, locationstart);


--
-- Name: i_geneticlocationfactmulti3; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactmulti3 ON geneticlocationfact USING btree (biosequenceob, mapname, chromosomename);


--
-- Name: i_geneticlocationfactmulti4; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactmulti4 ON geneticlocationfact USING btree (biosequenceob, mapname);


--
-- Name: i_geneticlocationfactseqid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactseqid ON geneticlocationfact USING btree (biosequenceob);


--
-- Name: i_geneticlocationlistlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationlistlsid ON geneticlocationlist USING btree (xreflsid);


--
-- Name: i_geneticoblistlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticoblistlsid ON geneticoblist USING btree (xreflsid);


--
-- Name: i_geneticoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticoblsid ON geneticob USING btree (xreflsid);


--
-- Name: i_geneticobsymbols; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticobsymbols ON geneticob USING btree (geneticobsymbols);


--
-- Name: i_genetictestfact2all; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genetictestfact2all ON genetictestfact2 USING btree (genetictestfact, factnamespace, attributename);


--
-- Name: i_genetictestfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genetictestfactlsid ON genetictestfact USING btree (xreflsid);


--
-- Name: i_genotpyestudysample1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotpyestudysample1 ON genotypestudy USING btree (biosampleob);


--
-- Name: i_genotypeobservationfact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotypeobservationfact1 ON genotypeobservationfact USING btree (genotypeobservation);


--
-- Name: i_genotypeobservationlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotypeobservationlsid ON genotypeobservation USING btree (xreflsid);


--
-- Name: i_genotypeobservationstudy1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotypeobservationstudy1 ON genotypeobservation USING btree (genotypestudy);


--
-- Name: i_genotypeobservationtest1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotypeobservationtest1 ON genotypeobservation USING btree (genetictestfact);


--
-- Name: i_genotypestudylsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotypestudylsid ON genotypestudy USING btree (xreflsid);


--
-- Name: i_geo_poolid1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geo_poolid1 ON geosubmissiondata USING btree (poolid1);


--
-- Name: i_gpl3802_probe_set_id; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gpl3802_probe_set_id ON gpl3802_annotation USING btree (probe_set_id);


--
-- Name: i_harvestwheatchip_annotation_ap; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_harvestwheatchip_annotation_ap ON harvestwheatchip_annotation USING btree (all_probes);


--
-- Name: i_importfunctionlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_importfunctionlsid ON importfunction USING btree (xreflsid);


--
-- Name: i_importprocedureoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_importprocedureoblsid ON importprocedureob USING btree (xreflsid);


--
-- Name: i_labresourcelistlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_labresourcelistlsid ON labresourcelist USING btree (xreflsid);


--
-- Name: i_labresourceoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_labresourceoblsid ON labresourceob USING btree (xreflsid);


--
-- Name: i_lisafanseriesnormalisation_0; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_lisafanseriesnormalisation_0 ON lisafanseriesnormalisation USING btree (datasourceob, voptypeid);


--
-- Name: i_listmembershipfact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_listmembershipfact1 ON listmembershipfact USING btree (memberid);


--
-- Name: i_listmembershipfact2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_listmembershipfact2 ON listmembershipfact USING btree (oblist, memberid);


--
-- Name: i_listmembershiplink_list; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_listmembershiplink_list ON listmembershiplink USING btree (oblist);


--
-- Name: i_listmembershipob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_listmembershipob ON listmembershiplink USING btree (ob);


--
-- Name: i_literaturereferenceoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_literaturereferenceoblsid ON literaturereferenceob USING btree (xreflsid);


--
-- Name: i_microarrayfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayfactlsid ON microarrayfact USING btree (xreflsid);


--
-- Name: i_microarrayobservationfactobs; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayobservationfactobs ON microarrayobservationfact USING btree (microarrayobservation);


--
-- Name: i_microarrayobslsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayobslsid ON microarrayobservation USING btree (xreflsid);


--
-- Name: i_microarrayspotfact_lrgal; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfact_lrgal ON microarrayspotfact USING btree (labresourceob, gal_name);


--
-- Name: i_microarrayspotfactaccession; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfactaccession ON microarrayspotfact USING btree (accession);


--
-- Name: i_microarrayspotfactgalid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfactgalid ON microarrayspotfact USING btree (gal_id);


--
-- Name: i_microarrayspotfactgene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfactgene ON microarrayspotfact USING btree (gal_genename);


--
-- Name: i_microarrayspotfactloc1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfactloc1 ON microarrayspotfact USING btree (labresourceob, gal_block, gal_column, gal_row);


--
-- Name: i_microarrayspotfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfactlsid ON microarrayspotfact USING btree (xreflsid);


--
-- Name: i_oblistlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_oblistlsid ON oblist USING btree (xreflsid);


--
-- Name: i_obxreflsid1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_obxreflsid1 ON ob USING btree (xreflsid);


--
-- Name: i_ontologyobname; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologyobname ON ontologyob USING btree (ontologyname);


--
-- Name: i_ontologyobxreflsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologyobxreflsid ON ontologyob USING btree (xreflsid);


--
-- Name: i_ontologytermfact2all; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfact2all ON ontologytermfact2 USING btree (factnamespace, attributename, attributevalue);


--
-- Name: i_ontologytermfact2av; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfact2av ON ontologytermfact2 USING btree (attributevalue);


--
-- Name: i_ontologytermfact2tav; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfact2tav ON ontologytermfact2 USING btree (ontologytermid, factnamespace, attributevalue);


--
-- Name: i_ontologytermfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfactlsid ON ontologytermfact USING btree (xreflsid);


--
-- Name: i_ontologytermfacto; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfacto ON ontologytermfact USING btree (ontologyob);


--
-- Name: i_ontologytermfactterm; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfactterm ON ontologytermfact USING btree (termname);


--
-- Name: i_oplsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_oplsid ON op USING btree (xreflsid);


--
-- Name: i_phenotypeobservationlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_phenotypeobservationlsid ON phenotypeobservation USING btree (xreflsid);


--
-- Name: i_phenotypestudylsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_phenotypestudylsid ON phenotypestudy USING btree (xreflsid);


--
-- Name: i_predicatelink1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_predicatelink1 ON predicatelink USING btree (objectob, subjectob, predicate);


--
-- Name: i_predicatelink2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_predicatelink2 ON predicatelink USING btree (subjectob, predicate);


--
-- Name: i_predicatelink3; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_predicatelink3 ON predicatelink USING btree (objectob, predicate);


--
-- Name: i_predicatelinklsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_predicatelinklsid ON predicatelink USING btree (xreflsid);


--
-- Name: i_securityfunction_ob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_securityfunction_ob ON securityfunction USING btree (ob);


--
-- Name: i_securityfunction_type; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_securityfunction_type ON securityfunction USING btree (applytotype);


--
-- Name: i_sequencealignmentfact_lsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_sequencealignmentfact_lsid ON sequencealignmentfact USING btree (xreflsid);


--
-- Name: i_sequencealignmentfact_ob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_sequencealignmentfact_ob ON sequencealignmentfact USING btree (databasesearchobservation);


--
-- Name: i_sequencingfunctionlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_sequencingfunctionlsid ON sequencingfunction USING btree (xreflsid);


--
-- Name: i_sequencingfunctionsample; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_sequencingfunctionsample ON sequencingfunction USING btree (biosampleob);


--
-- Name: i_sequencingfunctionseq; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_sequencingfunctionseq ON sequencingfunction USING btree (biosequenceob);


--
-- Name: i_staffoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_staffoblsid ON staffob USING btree (xreflsid);


--
-- Name: i_tanimalfact_animalid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_tanimalfact_animalid ON t_animal_fact USING btree (animalid);


--
-- Name: i_tanimalfact_ob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_tanimalfact_ob ON t_animal_fact USING btree (biosubjectob);


--
-- Name: i_tsamplefact_animalid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_tsamplefact_animalid ON t_sample_fact USING btree (animalid);


--
-- Name: i_tsamplefact_ob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_tsamplefact_ob ON t_sample_fact USING btree (biosubjectob);


--
-- Name: i_tsamplefact_sampleid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_tsamplefact_sampleid ON t_sample_fact USING btree (sampleid);


--
-- Name: i_uri_temp; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_uri_temp ON uriob USING btree (uristring);


--
-- Name: i_urilinkob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_urilinkob ON urilink USING btree (ob);


--
-- Name: i_urilinkoburiob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_urilinkoburiob ON urilink USING btree (uriob, ob);


--
-- Name: i_urilinkuriob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_urilinkuriob ON urilink USING btree (uriob);


--
-- Name: i_urilsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_urilsid ON uriob USING btree (xreflsid);


--
-- Name: i_wheatchipannotation2011_probeset; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_wheatchipannotation2011_probeset ON wheatchipannotation2011 USING btree (probeset);


--
-- Name: i_workflowlinklsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_workflowlinklsid ON workflowlink USING btree (xreflsid);


--
-- Name: i_workflowmembershiplinklsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_workflowmembershiplinklsid ON workflowmembershiplink USING btree (xreflsid);


--
-- Name: i_workflowoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_workflowoblsid ON workflowob USING btree (xreflsid);


--
-- Name: i_workflowstageoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_workflowstageoblsid ON workflowstageob USING btree (xreflsid);


--
-- Name: i_workstagevisitfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_workstagevisitfactlsid ON workstagevisitfact USING btree (xreflsid);


--
-- Name: ianneoconnelarrays2_p; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ianneoconnelarrays2_p ON anneoconnelarrays2 USING btree (dbprobes);


--
-- Name: ibt4wgsnppanel_v6_3cmarkernames1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ibt4wgsnppanel_v6_3cmarkernames1 ON bt4wgsnppanel_v6_3cmarkernames USING btree (name);


--
-- Name: ibt4wgsnppanel_v6_3cmarkernames2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ibt4wgsnppanel_v6_3cmarkernames2 ON bt4wgsnppanel_v6_3cmarkernames USING btree (onchipname);


--
-- Name: ics34clusterpaperdata_contig; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ics34clusterpaperdata_contig ON cs34clusterpaperdata USING btree (contigname);


--
-- Name: ifilerecgeosubmission; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ifilerecgeosubmission ON geosubmissiondata USING btree (filerecnum);


--
-- Name: igene_infogeneid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX igene_infogeneid ON gene_info USING btree (geneid);


--
-- Name: igene_infosymtax; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX igene_infosymtax ON gene_info USING btree (symbol, tax_id);


--
-- Name: igenotypes; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX igenotypes ON genotypes USING btree (snp_name);


--
-- Name: igpl7083_34008annotationensid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX igpl7083_34008annotationensid ON gpl7083_34008annotation USING btree (ensembl_id);


--
-- Name: igpl7083_34008annotationgbacc; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX igpl7083_34008annotationgbacc ON gpl7083_34008annotation USING btree (gb_acc);


--
-- Name: ihg18uniquereads_hit; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ihg18uniquereads_hit ON hg18uniquereads USING btree (mappedtofrag);


--
-- Name: ihg18uniquereads_query; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ihg18uniquereads_query ON hg18uniquereads USING btree (queryfrag);


--
-- Name: iimportfunction_ds; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iimportfunction_ds ON importfunction USING btree (datasourceob);


--
-- Name: iimportfunction_ob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iimportfunction_ob ON importfunction USING btree (ob);


--
-- Name: ijunk; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ijunk ON junk USING btree (obid);


--
-- Name: ijunk1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ijunk1 ON junk1 USING btree (datasourcelsid);


--
-- Name: ilicnormalisation1_probeset; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ilicnormalisation1_probeset ON licnormalisation1 USING btree (probeset);


--
-- Name: imicroarrayobservation_ms; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX imicroarrayobservation_ms ON microarrayobservation USING btree (microarraystudy);


--
-- Name: imicroarrayobservation_msf; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX imicroarrayobservation_msf ON microarrayobservation USING btree (microarrayspotfact);


--
-- Name: imicroarrayobservation_msfs; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX imicroarrayobservation_msfs ON microarrayobservation USING btree (microarraystudy, microarrayspotfact);


--
-- Name: iprint139annotation_en; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iprint139annotation_en ON print139annotation_v1 USING btree (estname);


--
-- Name: iprint139annotation_gn; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iprint139annotation_gn ON print139annotation_v1 USING btree (arraygene_name);


--
-- Name: iprint139annotationv1_c; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iprint139annotationv1_c ON print139annotation_v1 USING btree (contentid);


--
-- Name: ireproductionmicroarrayplasmids_mc; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ireproductionmicroarrayplasmids_mc ON reproductionmicroarrayplasmids USING btree (microarray_code);


--
-- Name: iseqname; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iseqname ON sheepv3_prot_annotation USING btree (seqname);


--
-- Name: ispotidmapcaco2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ispotidmapcaco2 ON spotidmapcaco2 USING btree (recnum);


--
-- Name: istart_hg18_cpg_mspi_overlap; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX istart_hg18_cpg_mspi_overlap ON hg18_cpg_mspi_overlap USING btree (chrom, start);


--
-- Name: istop_hg18_cpg_mspi_overlap; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX istop_hg18_cpg_mspi_overlap ON hg18_cpg_mspi_overlap USING btree (chrom, stop);


--
-- Name: isystem_blastn_results; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_blastn_results ON blastn_results USING btree (datasourceob, voptypeid);


--
-- Name: isystem_geosubmissiondata; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_geosubmissiondata ON geosubmissiondata USING btree (datasourceob, voptypeid);


--
-- Name: isystem_gpl3802_annotation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_gpl3802_annotation ON gpl3802_annotation USING btree (datasourceob, voptypeid);


--
-- Name: isystem_harvestwheatchip_annotation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_harvestwheatchip_annotation ON harvestwheatchip_annotation USING btree (datasourceob, voptypeid);


--
-- Name: isystem_sheepv3_prot_annotation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_sheepv3_prot_annotation ON sheepv3_prot_annotation USING btree (datasourceob, voptypeid);


--
-- Name: isystem_spotidmapcaco2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_spotidmapcaco2 ON spotidmapcaco2 USING btree (datasourceob, voptypeid);


--
-- Name: isystem_wheatchipannotation2011; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_wheatchipannotation2011 ON wheatchipannotation2011 USING btree (datasourceob, voptypeid);


--
-- Name: isystem_wheatrma; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_wheatrma ON wheatrma USING btree (datasourceob, voptypeid);


--
-- Name: isystemanneoconnelarrays2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemanneoconnelarrays2 ON anneoconnelarrays2 USING btree (datasourceob, voptypeid);


--
-- Name: isystemanneoconnelprobenames; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemanneoconnelprobenames ON anneoconnelprobenames USING btree (datasourceob, voptypeid);


--
-- Name: isystembt4wgsnppanel_v6_3cmarkernames; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystembt4wgsnppanel_v6_3cmarkernames ON bt4wgsnppanel_v6_3cmarkernames USING btree (datasourceob, voptypeid);


--
-- Name: isystemcpgfragmentsneargenes; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemcpgfragmentsneargenes ON cpgfragmentsneargenes USING btree (datasourceob, voptypeid);


--
-- Name: isystemcs34clusterpaperdata; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemcs34clusterpaperdata ON cs34clusterpaperdata USING btree (datasourceob, voptypeid);


--
-- Name: isystemdata_set_1_genstat_results_180908; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemdata_set_1_genstat_results_180908 ON data_set_1_genstat_results_180908 USING btree (datasourceob, voptypeid);


--
-- Name: isystemdata_set_2_r_results_180908; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemdata_set_2_r_results_180908 ON data_set_2_r_results_180908 USING btree (datasourceob, voptypeid);


--
-- Name: isystemgene2accession; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemgene2accession ON gene2accession USING btree (datasourceob, voptypeid);


--
-- Name: isystemgene_info; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemgene_info ON gene_info USING btree (datasourceob, voptypeid);


--
-- Name: isystemgenotypes; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemgenotypes ON genotypes USING btree (datasourceob, voptypeid);


--
-- Name: isystemgpl7083_34008annotation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemgpl7083_34008annotation ON gpl7083_34008annotation USING btree (datasourceob, voptypeid);


--
-- Name: isystemhg18_cpg_location; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemhg18_cpg_location ON hg18_cpg_location USING btree (datasourceob, voptypeid);


--
-- Name: isystemhg18_cpg_mspi_overlap; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemhg18_cpg_mspi_overlap ON hg18_cpg_mspi_overlap USING btree (datasourceob, voptypeid);


--
-- Name: isystemhg18_mspi_digest; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemhg18_mspi_digest ON hg18_mspi_digest USING btree (datasourceob, voptypeid);


--
-- Name: isystemhg18_refgenes_location; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemhg18_refgenes_location ON hg18_refgenes_location USING btree (datasourceob, voptypeid);


--
-- Name: isystemhg18uniquereads; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemhg18uniquereads ON hg18uniquereads USING btree (datasourceob, voptypeid);


--
-- Name: isystemlicexpression1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemlicexpression1 ON licexpression1 USING btree (datasourceob, voptypeid);


--
-- Name: isystemlicnormalisation1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemlicnormalisation1 ON licnormalisation1 USING btree (datasourceob, voptypeid);


--
-- Name: isystemlisafanseriesnormalisation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemlisafanseriesnormalisation ON lisafanseriesnormalisation USING btree (datasourceob, voptypeid);


--
-- Name: isystemoracle_microarray_experiment; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemoracle_microarray_experiment ON oracle_microarray_experiment USING btree (datasourceob, voptypeid);


--
-- Name: isystemprint139annotation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemprint139annotation ON print139annotation USING btree (datasourceob, voptypeid);


--
-- Name: isystemprint139annotation_v1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemprint139annotation_v1 ON print139annotation_v1 USING btree (datasourceob, voptypeid);


--
-- Name: isystemreproductionmicroarrayplasmids; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemreproductionmicroarrayplasmids ON reproductionmicroarrayplasmids USING btree (datasourceob, voptypeid);


--
-- Name: isystemtaxonomy_names; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemtaxonomy_names ON taxonomy_names USING btree (datasourceob, voptypeid);


--
-- Name: itax_id; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX itax_id ON taxonomy_names USING btree (tax_id);


--
-- Name: licexpression1gene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX licexpression1gene ON licexpression1 USING btree (affygene);


--
-- Name: lisafan_expt136_lowscan_no_bg_corr_gene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX lisafan_expt136_lowscan_no_bg_corr_gene ON lisafan_expt136_lowscan_no_bg_corr_delete01102008 USING btree (gene_name);


--
-- Name: lisafanseriesnormalisationgene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX lisafanseriesnormalisationgene ON lisafanseriesnormalisation USING btree (gene_name);


--
-- Name: print139annotationcontent; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX print139annotationcontent ON print139annotation USING btree (contentid);


--
-- Name: print139annotationestname; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX print139annotationestname ON print139annotation USING btree (estname);


--
-- Name: systemgeosubmissiondata; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX systemgeosubmissiondata ON geosubmissiondata USING btree (datasourceob, voptypeid);


--
-- Name: checkaccesslinkkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkaccesslinkkey
    BEFORE INSERT OR UPDATE ON accesslink
    FOR EACH ROW
    EXECUTE PROCEDURE checkaccesslinkkey();


--
-- Name: checkaccessontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkaccessontology
    BEFORE INSERT OR UPDATE ON accesslink
    FOR EACH ROW
    EXECUTE PROCEDURE checkaccessontology();


--
-- Name: checkaccessontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkaccessontology
    BEFORE INSERT OR UPDATE ON accessfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkaccessontology();


--
-- Name: checkaliquotrecord; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkaliquotrecord
    BEFORE INSERT OR UPDATE ON biosamplealiquotfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkaliquotrecord();


--
-- Name: checkanalysisfunctionobkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkanalysisfunctionobkey
    BEFORE INSERT OR UPDATE ON analysisfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checkanalysisfunctionobkey();


--
-- Name: checkanalysistypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkanalysistypeontology
    BEFORE INSERT OR UPDATE ON analysisprocedureob
    FOR EACH ROW
    EXECUTE PROCEDURE checkanalysistypeontology();


--
-- Name: checkbiodatabasetypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkbiodatabasetypeontology
    BEFORE INSERT OR UPDATE ON biodatabaseob
    FOR EACH ROW
    EXECUTE PROCEDURE checkbiodatabasetype();


--
-- Name: checkbiolibrarytypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkbiolibrarytypeontology
    BEFORE INSERT OR UPDATE ON biolibraryob
    FOR EACH ROW
    EXECUTE PROCEDURE checkbiolibrarytypeontology();


--
-- Name: checkbioprotocoltypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkbioprotocoltypeontology
    BEFORE INSERT OR UPDATE ON bioprotocolob
    FOR EACH ROW
    EXECUTE PROCEDURE checkbioprotocoltypeontology();


--
-- Name: checkbiosampletypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkbiosampletypeontology
    BEFORE INSERT OR UPDATE ON biosampleob
    FOR EACH ROW
    EXECUTE PROCEDURE checkbiosampletypeontology();


--
-- Name: checkcommentedobkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkcommentedobkey
    BEFORE INSERT OR UPDATE ON commentob
    FOR EACH ROW
    EXECUTE PROCEDURE checkcommentedobkey();


--
-- Name: checkcommentlinkkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkcommentlinkkey
    BEFORE INSERT OR UPDATE ON commentlink
    FOR EACH ROW
    EXECUTE PROCEDURE checkcommentlinkkey();


--
-- Name: checkdatabasesearchstudytypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkdatabasesearchstudytypeontology
    BEFORE INSERT OR UPDATE ON databasesearchstudy
    FOR EACH ROW
    EXECUTE PROCEDURE checkdatabasesearchstudytypeontology();


--
-- Name: checkdatasourceontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkdatasourceontology
    BEFORE INSERT OR UPDATE ON datasourceob
    FOR EACH ROW
    EXECUTE PROCEDURE checkdatasourceontology();


--
-- Name: checkdfvoptypeid; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkdfvoptypeid
    BEFORE INSERT OR UPDATE ON displayfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checkvoptypeid();


--
-- Name: checkdisplayfunctionobkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkdisplayfunctionobkey
    BEFORE INSERT OR UPDATE ON displayfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checkdisplayfunctionobkey();


--
-- Name: checkenotypestudytypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkenotypestudytypeontology
    BEFORE INSERT OR UPDATE ON genotypestudy
    FOR EACH ROW
    EXECUTE PROCEDURE checkgenotypestudytypeontology();


--
-- Name: checkfeatureattributeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkfeatureattributeontology
    BEFORE INSERT OR UPDATE ON biosequencefeatureattributefact
    FOR EACH ROW
    EXECUTE PROCEDURE checkfeatureattributeontology();


--
-- Name: checkfeatureontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkfeatureontology
    BEFORE INSERT OR UPDATE ON biosequencefeaturefact
    FOR EACH ROW
    EXECUTE PROCEDURE checkfeatureontology();


--
-- Name: checkgeneexpressionstudytypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkgeneexpressionstudytypeontology
    BEFORE INSERT OR UPDATE ON geneexpressionstudy
    FOR EACH ROW
    EXECUTE PROCEDURE checkgeneexpressionstudytypeontology();


--
-- Name: checkgeneticlistontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkgeneticlistontology
    BEFORE INSERT OR UPDATE ON geneticoblist
    FOR EACH ROW
    EXECUTE PROCEDURE checkgeneticlistontology();


--
-- Name: checkgeneticobontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkgeneticobontology
    BEFORE INSERT OR UPDATE ON geneticob
    FOR EACH ROW
    EXECUTE PROCEDURE checkgeneticobontology();


--
-- Name: checkgenetictestontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkgenetictestontology
    BEFORE INSERT OR UPDATE ON genetictestfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkgenetictestontology();


--
-- Name: checkimportobkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkimportobkey
    BEFORE INSERT OR UPDATE ON importfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checkimportobkey();


--
-- Name: checklfvoptypeid; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checklfvoptypeid
    BEFORE INSERT OR UPDATE ON listmembershipfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkvoptypeid();


--
-- Name: checkliteraturereferencelinkkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkliteraturereferencelinkkey
    BEFORE INSERT OR UPDATE ON literaturereferencelink
    FOR EACH ROW
    EXECUTE PROCEDURE checkliteraturereferencelinkkey();


--
-- Name: checklmvoptypeid; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checklmvoptypeid
    BEFORE INSERT OR UPDATE ON listmembershiplink
    FOR EACH ROW
    EXECUTE PROCEDURE checkvoptypeid();


--
-- Name: checkoblistkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkoblistkey
    BEFORE INSERT OR UPDATE ON listmembershiplink
    FOR EACH ROW
    EXECUTE PROCEDURE checkoblistkey();


--
-- Name: checkontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkontology
    BEFORE INSERT OR UPDATE ON predicatelink
    FOR EACH ROW
    EXECUTE PROCEDURE checkpredicateontology();


--
-- Name: checkontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkontology
    BEFORE INSERT OR UPDATE ON oblist
    FOR EACH ROW
    EXECUTE PROCEDURE checklistontology();


--
-- Name: checkontologyunitname; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkontologyunitname
    BEFORE INSERT OR UPDATE ON ontologytermfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkunitname();


--
-- Name: checkpedigreeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkpedigreeontology
    BEFORE INSERT OR UPDATE ON pedigreelink
    FOR EACH ROW
    EXECUTE PROCEDURE checkpedigreeontology();


--
-- Name: checkphenotypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkphenotypeontology
    BEFORE INSERT OR UPDATE ON phenotypeobservation
    FOR EACH ROW
    EXECUTE PROCEDURE checkphenotypeontology();


--
-- Name: checkphenotypeontologyname; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkphenotypeontologyname
    BEFORE INSERT OR UPDATE ON phenotypestudy
    FOR EACH ROW
    EXECUTE PROCEDURE checkphenotypeontologyname();


--
-- Name: checkpredicatekeys; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkpredicatekeys
    BEFORE INSERT OR UPDATE ON predicatelink
    FOR EACH ROW
    EXECUTE PROCEDURE checkpredicatekeys();


--
-- Name: checksampleunits; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checksampleunits
    BEFORE INSERT OR UPDATE ON biosampleob
    FOR EACH ROW
    EXECUTE PROCEDURE checksampleunits();


--
-- Name: checksamplingunitname; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checksamplingunitname
    BEFORE INSERT OR UPDATE ON biosamplingfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkunitname();


--
-- Name: checksecurityfunctionobkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checksecurityfunctionobkey
    BEFORE INSERT OR UPDATE ON securityfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checksecurityfunctionobkey();


--
-- Name: checksequenceontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checksequenceontology
    BEFORE INSERT OR UPDATE ON biosequenceob
    FOR EACH ROW
    EXECUTE PROCEDURE checksequenceontology();


--
-- Name: checksfvoptypeid; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checksfvoptypeid
    BEFORE INSERT OR UPDATE ON sequencingfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checkvoptypeid();


--
-- Name: checkurilinkkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkurilinkkey
    BEFORE INSERT OR UPDATE ON urilink
    FOR EACH ROW
    EXECUTE PROCEDURE checkurilinkkey();


--
-- Name: checkworkflowontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkworkflowontology
    BEFORE INSERT OR UPDATE ON workflowstageob
    FOR EACH ROW
    EXECUTE PROCEDURE checkworkflowontology();


--
-- Name: filterkeywords; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER filterkeywords
    BEFORE INSERT OR UPDATE ON ob
    FOR EACH ROW
    EXECUTE PROCEDURE filterkeywords('obkeywords');


--
-- Name: filterkeywords; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER filterkeywords
    BEFORE INSERT OR UPDATE ON biosubjectob
    FOR EACH ROW
    EXECUTE PROCEDURE filterkeywords('obkeywords');


--
-- Name: filterkeywords; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER filterkeywords
    BEFORE INSERT OR UPDATE ON microarrayspotfact
    FOR EACH ROW
    EXECUTE PROCEDURE filterkeywords('obkeywords');


--
-- Name: labresourcetypecheck; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER labresourcetypecheck
    BEFORE INSERT OR UPDATE ON labresourceob
    FOR EACH ROW
    EXECUTE PROCEDURE checklabresourceontology();


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON ontologyob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('5');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON ontologytermfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('10');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON predicatelink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('15');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON oblist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('20');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON uriob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('30');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON commentob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('40');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON staffob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('50');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON literaturereferenceob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('60');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON labresourceob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('70');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON labresourcelist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('75');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosubjectob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('85');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosampleob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('90');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON bioprotocolob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('95');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosamplingfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('100');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosamplelist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('102');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON pedigreelink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('335');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosequenceob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('115');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosequencefeaturefact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('117');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON sequencingfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('120');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON datasourceob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('125');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON importprocedureob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('130');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON importfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('135');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON displayprocedureob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('140');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON displayfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('145');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON phenotypestudy
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('150');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON phenotypeobservation
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('155');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('160');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticoblist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('165');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticfunctionfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('190');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticexpressionfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('195');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('200');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneproductlink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('201');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON generegulationlink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('202');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON genotypestudy
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('290');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON genetictestfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('305');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON genotypeobservation
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('300');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticlocationfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('175');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticlocationlist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('180');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON workflowob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('205');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON workflowstageob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('210');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON workstagevisitfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('225');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON workflowmembershiplink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('215');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON workflowlink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('220');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON microarrayfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('230');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON microarrayspotfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('235');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneexpressionstudy
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('240');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON microarrayobservation
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('250');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biodatabaseob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('315');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON databasesearchstudy
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('320');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON databasesearchobservation
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('325');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON sequencealignmentfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('330');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosamplealiquotfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('400');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON securityprocedureob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('460');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON securityfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('465');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biolibraryob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('485');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biolibraryconstructionfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('495');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON librarysequencingfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('500');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON analysisprocedureob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('540');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON datasourcelist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('550');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON analysisfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('545');


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ob
    ADD CONSTRAINT "$1" FOREIGN KEY (obtypeid) REFERENCES obtype(obtypeid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY obtypesignature
    ADD CONSTRAINT "$1" FOREIGN KEY (obtypeid) REFERENCES obtype(obtypeid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY op
    ADD CONSTRAINT "$1" FOREIGN KEY (voptypeid) REFERENCES obtype(obtypeid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY optypesignature
    ADD CONSTRAINT "$1" FOREIGN KEY (obtypeid) REFERENCES obtype(obtypeid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologyfact
    ADD CONSTRAINT "$1" FOREIGN KEY (ontologyob) REFERENCES ontologyob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologytermfact2
    ADD CONSTRAINT "$1" FOREIGN KEY (ontologytermid) REFERENCES ontologytermfact(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY predicatelinkfact
    ADD CONSTRAINT "$1" FOREIGN KEY (predicatelink) REFERENCES predicatelink(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY listmembershiplink
    ADD CONSTRAINT "$1" FOREIGN KEY (oblist) REFERENCES oblist(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY oblistfact
    ADD CONSTRAINT "$1" FOREIGN KEY (listob) REFERENCES oblist(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY urilink
    ADD CONSTRAINT "$1" FOREIGN KEY (uriob) REFERENCES uriob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY commentlink
    ADD CONSTRAINT "$1" FOREIGN KEY (commentob) REFERENCES commentob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY accesslink
    ADD CONSTRAINT "$1" FOREIGN KEY (ob) REFERENCES ob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY stafffact
    ADD CONSTRAINT "$1" FOREIGN KEY (staffob) REFERENCES staffob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY accessfact
    ADD CONSTRAINT "$1" FOREIGN KEY (ob) REFERENCES ob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY literaturereferencelink
    ADD CONSTRAINT "$1" FOREIGN KEY (literaturereferenceob) REFERENCES literaturereferenceob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourcefact
    ADD CONSTRAINT "$1" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourcelistmembershiplink
    ADD CONSTRAINT "$1" FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectfact
    ADD CONSTRAINT "$1" FOREIGN KEY (biosubjectob) REFERENCES biosubjectob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplefact
    ADD CONSTRAINT "$1" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfact
    ADD CONSTRAINT "$1" FOREIGN KEY (biosamplingfunction) REFERENCES biosamplingfunction(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplelistmembershiplink
    ADD CONSTRAINT "$1" FOREIGN KEY (biosamplelist) REFERENCES biosamplelist(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefact
    ADD CONSTRAINT "$1" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeatureattributefact
    ADD CONSTRAINT "$1" FOREIGN KEY (biosequencefeaturefact) REFERENCES biosequencefeaturefact(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfact
    ADD CONSTRAINT "$1" FOREIGN KEY (sequencingfunction) REFERENCES sequencingfunction(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourcefact
    ADD CONSTRAINT "$1" FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importfunctionfact
    ADD CONSTRAINT "$1" FOREIGN KEY (importfunction) REFERENCES importfunction(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticoblistmembershiplink
    ADD CONSTRAINT "$1" FOREIGN KEY (geneticoblist) REFERENCES geneticoblist(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudyfact
    ADD CONSTRAINT "$1" FOREIGN KEY (genotypestudy) REFERENCES genotypestudy(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypeobservationfact
    ADD CONSTRAINT "$1" FOREIGN KEY (genotypeobservation) REFERENCES genotypeobservation(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationlistmembershiplink
    ADD CONSTRAINT "$1" FOREIGN KEY (geneticlocationlist) REFERENCES geneticlocationlist(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayfact
    ADD CONSTRAINT "$1" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY miamefact
    ADD CONSTRAINT "$1" FOREIGN KEY (microarraystudy) REFERENCES geneexpressionstudy(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneexpressionstudyfact
    ADD CONSTRAINT "$1" FOREIGN KEY (geneexpressionstudy) REFERENCES geneexpressionstudy(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayobservationfact
    ADD CONSTRAINT "$1" FOREIGN KEY (microarrayobservation) REFERENCES microarrayobservation(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplealiquotfact2
    ADD CONSTRAINT "$1" FOREIGN KEY (biosamplealiquotfact) REFERENCES biosamplealiquotfact(obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genetictestfact2
    ADD CONSTRAINT "$1" FOREIGN KEY (genetictestfact) REFERENCES genetictestfact(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ob
    ADD CONSTRAINT "$2" FOREIGN KEY (statuscode) REFERENCES obstatus(statuscode);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY obtypesignature
    ADD CONSTRAINT "$2" FOREIGN KEY (mandatoryoptype) REFERENCES obtype(obtypeid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY optypesignature
    ADD CONSTRAINT "$2" FOREIGN KEY (argobtypeid) REFERENCES obtype(obtypeid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologytermfact
    ADD CONSTRAINT "$2" FOREIGN KEY (ontologyob) REFERENCES ontologyob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY accesslink
    ADD CONSTRAINT "$2" FOREIGN KEY (staffob) REFERENCES staffob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourcelistmembershiplink
    ADD CONSTRAINT "$2" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT "$2" FOREIGN KEY (biosubjectob) REFERENCES biosubjectob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplelistmembershiplink
    ADD CONSTRAINT "$2" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY pedigreelink
    ADD CONSTRAINT "$2" FOREIGN KEY (subjectob) REFERENCES biosubjectob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact
    ADD CONSTRAINT "$2" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT "$2" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importfunction
    ADD CONSTRAINT "$2" FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction
    ADD CONSTRAINT "$2" FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation
    ADD CONSTRAINT "$2" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticoblistmembershiplink
    ADD CONSTRAINT "$2" FOREIGN KEY (geneticob) REFERENCES geneticob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfunctionfact
    ADD CONSTRAINT "$2" FOREIGN KEY (geneticob) REFERENCES geneticob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact
    ADD CONSTRAINT "$2" FOREIGN KEY (geneticob) REFERENCES geneticob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact
    ADD CONSTRAINT "$2" FOREIGN KEY (geneticob) REFERENCES geneticob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneproductlink
    ADD CONSTRAINT "$2" FOREIGN KEY (geneticob) REFERENCES geneticob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY generegulationlink
    ADD CONSTRAINT "$2" FOREIGN KEY (geneticob) REFERENCES geneticob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT "$2" FOREIGN KEY (biosamplelist) REFERENCES biosamplelist(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genetictestfact
    ADD CONSTRAINT "$2" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypeobservation
    ADD CONSTRAINT "$2" FOREIGN KEY (genotypestudy) REFERENCES genotypestudy(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationlistmembershiplink
    ADD CONSTRAINT "$2" FOREIGN KEY (geneticlocationfact) REFERENCES geneticlocationfact(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact
    ADD CONSTRAINT "$2" FOREIGN KEY (workflowstage) REFERENCES workflowstageob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowmembershiplink
    ADD CONSTRAINT "$2" FOREIGN KEY (workflowob) REFERENCES workflowob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowlink
    ADD CONSTRAINT "$2" FOREIGN KEY (fromstage) REFERENCES workflowstageob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayspotfact
    ADD CONSTRAINT "$2" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneexpressionstudy
    ADD CONSTRAINT "$2" FOREIGN KEY (biosamplelist) REFERENCES biosamplelist(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayobservation
    ADD CONSTRAINT "$2" FOREIGN KEY (microarraystudy) REFERENCES geneexpressionstudy(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchstudy
    ADD CONSTRAINT "$2" FOREIGN KEY (biodatabaseob) REFERENCES biodatabaseob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation
    ADD CONSTRAINT "$2" FOREIGN KEY (databasesearchstudy) REFERENCES databasesearchstudy(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencealignmentfact
    ADD CONSTRAINT "$2" FOREIGN KEY (databasesearchobservation) REFERENCES databasesearchobservation(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplealiquotfact
    ADD CONSTRAINT "$2" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityfunction
    ADD CONSTRAINT "$2" FOREIGN KEY (applytotype) REFERENCES obtype(obtypeid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY accesslink
    ADD CONSTRAINT "$3" FOREIGN KEY (oblist) REFERENCES oblist(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT "$3" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY pedigreelink
    ADD CONSTRAINT "$3" FOREIGN KEY (objectob) REFERENCES biosubjectob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT "$3" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importfunction
    ADD CONSTRAINT "$3" FOREIGN KEY (importprocedureob) REFERENCES importprocedureob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction
    ADD CONSTRAINT "$3" FOREIGN KEY (displayprocedureob) REFERENCES displayprocedureob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation
    ADD CONSTRAINT "$3" FOREIGN KEY (biosamplelist) REFERENCES biosamplelist(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact
    ADD CONSTRAINT "$3" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneproductlink
    ADD CONSTRAINT "$3" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY generegulationlink
    ADD CONSTRAINT "$3" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT "$3" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypeobservation
    ADD CONSTRAINT "$3" FOREIGN KEY (genetictestfact) REFERENCES genetictestfact(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowmembershiplink
    ADD CONSTRAINT "$3" FOREIGN KEY (workflowstageob) REFERENCES workflowstageob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowlink
    ADD CONSTRAINT "$3" FOREIGN KEY (tostage) REFERENCES workflowstageob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneexpressionstudy
    ADD CONSTRAINT "$3" FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayobservation
    ADD CONSTRAINT "$3" FOREIGN KEY (microarrayspotfact) REFERENCES microarrayspotfact(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchstudy
    ADD CONSTRAINT "$3" FOREIGN KEY (bioprotocolob) REFERENCES bioprotocolob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation
    ADD CONSTRAINT "$3" FOREIGN KEY (querysequence) REFERENCES biosequenceob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY securityfunction
    ADD CONSTRAINT "$3" FOREIGN KEY (securityprocedureob) REFERENCES securityprocedureob(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT "$4" FOREIGN KEY (bioprotocolob) REFERENCES bioprotocolob(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT "$4" FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation
    ADD CONSTRAINT "$4" FOREIGN KEY (biosubjectob) REFERENCES biosubjectob(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT "$4" FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact
    ADD CONSTRAINT "$4" FOREIGN KEY (geneticob) REFERENCES geneticob(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneexpressionstudy
    ADD CONSTRAINT "$4" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation
    ADD CONSTRAINT "$4" FOREIGN KEY (hitsequence) REFERENCES biosequenceob(obid);


--
-- Name: $5; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT "$5" FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: $5; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT "$5" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: $5; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation
    ADD CONSTRAINT "$5" FOREIGN KEY (phenotypestudy) REFERENCES phenotypestudy(obid);


--
-- Name: $5; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT "$5" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: $5; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact
    ADD CONSTRAINT "$5" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


--
-- Name: $5; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneexpressionstudy
    ADD CONSTRAINT "$5" FOREIGN KEY (bioprotocolob) REFERENCES bioprotocolob(obid);


--
-- Name: $6; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT "$6" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: $6; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT "$6" FOREIGN KEY (bioprotocolob) REFERENCES bioprotocolob(obid);


--
-- Name: $6; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact
    ADD CONSTRAINT "$6" FOREIGN KEY (genetictestfact) REFERENCES genetictestfact(obid);


--
-- Name: analysisfunction_analysisprocedureob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction
    ADD CONSTRAINT analysisfunction_analysisprocedureob_fkey FOREIGN KEY (analysisprocedureob) REFERENCES analysisprocedureob(obid);


--
-- Name: analysisfunction_datasourcelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction
    ADD CONSTRAINT analysisfunction_datasourcelist_fkey FOREIGN KEY (datasourcelist) REFERENCES datasourcelist(obid);


--
-- Name: analysisfunction_datasourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction
    ADD CONSTRAINT analysisfunction_datasourceob_fkey FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


--
-- Name: analysisprocedurefact_analysisprocedureob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisprocedurefact
    ADD CONSTRAINT analysisprocedurefact_analysisprocedureob_fkey FOREIGN KEY (analysisprocedureob) REFERENCES analysisprocedureob(obid);


--
-- Name: biodatabasefact_biodatabaseob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biodatabasefact
    ADD CONSTRAINT biodatabasefact_biodatabaseob_fkey FOREIGN KEY (biodatabaseob) REFERENCES biodatabaseob(obid);


--
-- Name: biolibraryconstructionfunction_biolibraryob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_biolibraryob_fkey FOREIGN KEY (biolibraryob) REFERENCES biolibraryob(obid);


--
-- Name: biolibraryconstructionfunction_bioprotocolob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_bioprotocolob_fkey FOREIGN KEY (bioprotocolob) REFERENCES bioprotocolob(obid);


--
-- Name: biolibraryconstructionfunction_biosampleob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_biosampleob_fkey FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: biolibraryconstructionfunction_labresourcelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_labresourcelist_fkey FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: biolibraryconstructionfunction_labresourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_labresourceob_fkey FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: biolibraryfact_biolibraryob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryfact
    ADD CONSTRAINT biolibraryfact_biolibraryob_fkey FOREIGN KEY (biolibraryob) REFERENCES biolibraryob(obid);


--
-- Name: biosubjectfk; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY t_animal_fact
    ADD CONSTRAINT biosubjectfk FOREIGN KEY (biosubjectob) REFERENCES biosubjectob(obid);


--
-- Name: biosubjectfk; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY t_sample_fact
    ADD CONSTRAINT biosubjectfk FOREIGN KEY (biosubjectob) REFERENCES biosubjectob(obid);


--
-- Name: datasourcelistmembershiplink_datasourcelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourcelistmembershiplink
    ADD CONSTRAINT datasourcelistmembershiplink_datasourcelist_fkey FOREIGN KEY (datasourcelist) REFERENCES datasourcelist(obid);


--
-- Name: datasourcelistmembershiplink_datasourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourcelistmembershiplink
    ADD CONSTRAINT datasourcelistmembershiplink_datasourceob_fkey FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


--
-- Name: gbs_sampleid_history_fact_biosampleob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbs_sampleid_history_fact
    ADD CONSTRAINT gbs_sampleid_history_fact_biosampleob_fkey FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: gbskeyfilebiosubjectfk; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbskeyfilefact
    ADD CONSTRAINT gbskeyfilebiosubjectfk FOREIGN KEY (biosubjectob) REFERENCES biosubjectob(obid);


--
-- Name: gbskeyfilefact_barcodedsampleob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbskeyfilefact
    ADD CONSTRAINT gbskeyfilefact_barcodedsampleob_fkey FOREIGN KEY (barcodedsampleob) REFERENCES biosampleob(obid);


--
-- Name: gbskeyfilefact_biosampleob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbskeyfilefact
    ADD CONSTRAINT gbskeyfilefact_biosampleob_fkey FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: gbsyieldfact_biosamplelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbsyieldfact
    ADD CONSTRAINT gbsyieldfact_biosamplelist_fkey FOREIGN KEY (biosamplelist) REFERENCES biosamplelist(obid);


--
-- Name: gbsyieldfact_biosampleob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbsyieldfact
    ADD CONSTRAINT gbsyieldfact_biosampleob_fkey FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: geneticlocationfact_mapobid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact
    ADD CONSTRAINT geneticlocationfact_mapobid_fkey FOREIGN KEY (mapobid) REFERENCES biosequenceob(obid);


--
-- Name: gpl3802_annotation_datasourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gpl3802_annotation
    ADD CONSTRAINT gpl3802_annotation_datasourceob_fkey FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


--
-- Name: gpl3802_annotation_voptypeid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gpl3802_annotation
    ADD CONSTRAINT gpl3802_annotation_voptypeid_fkey FOREIGN KEY (voptypeid) REFERENCES obtype(obtypeid);


--
-- Name: hiseqsamplesheetfact_biosamplelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY hiseqsamplesheetfact
    ADD CONSTRAINT hiseqsamplesheetfact_biosamplelist_fkey FOREIGN KEY (biosamplelist) REFERENCES biosamplelist(obid);


--
-- Name: librarysequencingfact_librarysequencingfunction_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfact
    ADD CONSTRAINT librarysequencingfact_librarysequencingfunction_fkey FOREIGN KEY (librarysequencingfunction) REFERENCES librarysequencingfunction(obid);


--
-- Name: librarysequencingfunction_biolibraryob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_biolibraryob_fkey FOREIGN KEY (biolibraryob) REFERENCES biolibraryob(obid);


--
-- Name: librarysequencingfunction_bioprotocolob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_bioprotocolob_fkey FOREIGN KEY (bioprotocolob) REFERENCES bioprotocolob(obid);


--
-- Name: librarysequencingfunction_datasourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_datasourceob_fkey FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


--
-- Name: librarysequencingfunction_labresourcelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_labresourcelist_fkey FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: librarysequencingfunction_labresourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_labresourceob_fkey FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: listmembershipfact_oblist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY listmembershipfact
    ADD CONSTRAINT listmembershipfact_oblist_fkey FOREIGN KEY (oblist) REFERENCES oblist(obid);


--
-- Name: sequencingfunction_biolibraryob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT sequencingfunction_biolibraryob_fkey FOREIGN KEY (biolibraryob) REFERENCES biolibraryob(obid);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: accessfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE accessfact FROM PUBLIC;
REVOKE ALL ON TABLE accessfact FROM agrbrdf;
GRANT ALL ON TABLE accessfact TO agrbrdf;
GRANT SELECT ON TABLE accessfact TO gbs;


--
-- Name: accesslink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE accesslink FROM PUBLIC;
REVOKE ALL ON TABLE accesslink FROM agrbrdf;
GRANT ALL ON TABLE accesslink TO agrbrdf;
GRANT SELECT ON TABLE accesslink TO gbs;


--
-- Name: ob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE ob FROM PUBLIC;
REVOKE ALL ON TABLE ob FROM agrbrdf;
GRANT ALL ON TABLE ob TO agrbrdf;
GRANT SELECT ON TABLE ob TO gbs;


--
-- Name: op; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE op FROM PUBLIC;
REVOKE ALL ON TABLE op FROM agrbrdf;
GRANT ALL ON TABLE op TO agrbrdf;
GRANT SELECT ON TABLE op TO gbs;


--
-- Name: analysisfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE analysisfunction FROM PUBLIC;
REVOKE ALL ON TABLE analysisfunction FROM agrbrdf;
GRANT ALL ON TABLE analysisfunction TO agrbrdf;
GRANT SELECT ON TABLE analysisfunction TO gbs;


--
-- Name: analysisprocedurefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE analysisprocedurefact FROM PUBLIC;
REVOKE ALL ON TABLE analysisprocedurefact FROM agrbrdf;
GRANT ALL ON TABLE analysisprocedurefact TO agrbrdf;
GRANT SELECT ON TABLE analysisprocedurefact TO gbs;


--
-- Name: analysisprocedureob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE analysisprocedureob FROM PUBLIC;
REVOKE ALL ON TABLE analysisprocedureob FROM agrbrdf;
GRANT ALL ON TABLE analysisprocedureob TO agrbrdf;
GRANT SELECT ON TABLE analysisprocedureob TO gbs;


--
-- Name: anneoconnelarrays2; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE anneoconnelarrays2 FROM PUBLIC;
REVOKE ALL ON TABLE anneoconnelarrays2 FROM agrbrdf;
GRANT ALL ON TABLE anneoconnelarrays2 TO agrbrdf;
GRANT SELECT ON TABLE anneoconnelarrays2 TO gbs;


--
-- Name: anneoconnelprobenames; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE anneoconnelprobenames FROM PUBLIC;
REVOKE ALL ON TABLE anneoconnelprobenames FROM agrbrdf;
GRANT ALL ON TABLE anneoconnelprobenames TO agrbrdf;
GRANT SELECT ON TABLE anneoconnelprobenames TO gbs;


--
-- Name: anneoconnelprobenames_bak; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE anneoconnelprobenames_bak FROM PUBLIC;
REVOKE ALL ON TABLE anneoconnelprobenames_bak FROM agrbrdf;
GRANT ALL ON TABLE anneoconnelprobenames_bak TO agrbrdf;
GRANT SELECT ON TABLE anneoconnelprobenames_bak TO gbs;


--
-- Name: arrayexpressorthologs; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE arrayexpressorthologs FROM PUBLIC;
REVOKE ALL ON TABLE arrayexpressorthologs FROM agrbrdf;
GRANT ALL ON TABLE arrayexpressorthologs TO agrbrdf;
GRANT SELECT ON TABLE arrayexpressorthologs TO gbs;


--
-- Name: biodatabasefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biodatabasefact FROM PUBLIC;
REVOKE ALL ON TABLE biodatabasefact FROM agrbrdf;
GRANT ALL ON TABLE biodatabasefact TO agrbrdf;
GRANT SELECT ON TABLE biodatabasefact TO gbs;


--
-- Name: biodatabaseob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biodatabaseob FROM PUBLIC;
REVOKE ALL ON TABLE biodatabaseob FROM agrbrdf;
GRANT ALL ON TABLE biodatabaseob TO agrbrdf;
GRANT SELECT ON TABLE biodatabaseob TO gbs;


--
-- Name: biolibraryconstructionfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biolibraryconstructionfunction FROM PUBLIC;
REVOKE ALL ON TABLE biolibraryconstructionfunction FROM agrbrdf;
GRANT ALL ON TABLE biolibraryconstructionfunction TO agrbrdf;
GRANT SELECT ON TABLE biolibraryconstructionfunction TO gbs;


--
-- Name: biolibraryfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biolibraryfact FROM PUBLIC;
REVOKE ALL ON TABLE biolibraryfact FROM agrbrdf;
GRANT ALL ON TABLE biolibraryfact TO agrbrdf;
GRANT SELECT ON TABLE biolibraryfact TO gbs;


--
-- Name: biolibraryob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biolibraryob FROM PUBLIC;
REVOKE ALL ON TABLE biolibraryob FROM agrbrdf;
GRANT ALL ON TABLE biolibraryob TO agrbrdf;
GRANT SELECT ON TABLE biolibraryob TO gbs;


--
-- Name: bioprotocolob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE bioprotocolob FROM PUBLIC;
REVOKE ALL ON TABLE bioprotocolob FROM agrbrdf;
GRANT ALL ON TABLE bioprotocolob TO agrbrdf;
GRANT SELECT ON TABLE bioprotocolob TO gbs;


--
-- Name: biosamplealiquotfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplealiquotfact FROM PUBLIC;
REVOKE ALL ON TABLE biosamplealiquotfact FROM agrbrdf;
GRANT ALL ON TABLE biosamplealiquotfact TO agrbrdf;
GRANT SELECT ON TABLE biosamplealiquotfact TO gbs;


--
-- Name: biosamplealiquotfact2; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplealiquotfact2 FROM PUBLIC;
REVOKE ALL ON TABLE biosamplealiquotfact2 FROM agrbrdf;
GRANT ALL ON TABLE biosamplealiquotfact2 TO agrbrdf;
GRANT SELECT ON TABLE biosamplealiquotfact2 TO gbs;


--
-- Name: biosamplefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplefact FROM PUBLIC;
REVOKE ALL ON TABLE biosamplefact FROM agrbrdf;
GRANT ALL ON TABLE biosamplefact TO agrbrdf;
GRANT SELECT ON TABLE biosamplefact TO gbs;


--
-- Name: biosamplelist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplelist FROM PUBLIC;
REVOKE ALL ON TABLE biosamplelist FROM agrbrdf;
GRANT ALL ON TABLE biosamplelist TO agrbrdf;
GRANT SELECT ON TABLE biosamplelist TO gbs;


--
-- Name: biosamplelistmembershiplink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplelistmembershiplink FROM PUBLIC;
REVOKE ALL ON TABLE biosamplelistmembershiplink FROM agrbrdf;
GRANT ALL ON TABLE biosamplelistmembershiplink TO agrbrdf;
GRANT SELECT ON TABLE biosamplelistmembershiplink TO gbs;


--
-- Name: biosampleob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosampleob FROM PUBLIC;
REVOKE ALL ON TABLE biosampleob FROM agrbrdf;
GRANT ALL ON TABLE biosampleob TO agrbrdf;
GRANT SELECT ON TABLE biosampleob TO gbs;


--
-- Name: biosamplingfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplingfact FROM PUBLIC;
REVOKE ALL ON TABLE biosamplingfact FROM agrbrdf;
GRANT ALL ON TABLE biosamplingfact TO agrbrdf;
GRANT SELECT ON TABLE biosamplingfact TO gbs;


--
-- Name: biosamplingfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplingfunction FROM PUBLIC;
REVOKE ALL ON TABLE biosamplingfunction FROM agrbrdf;
GRANT ALL ON TABLE biosamplingfunction TO agrbrdf;
GRANT SELECT ON TABLE biosamplingfunction TO gbs;


--
-- Name: biosequencefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosequencefact FROM PUBLIC;
REVOKE ALL ON TABLE biosequencefact FROM agrbrdf;
GRANT ALL ON TABLE biosequencefact TO agrbrdf;
GRANT SELECT ON TABLE biosequencefact TO gbs;


--
-- Name: biosequencefeatureattributefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosequencefeatureattributefact FROM PUBLIC;
REVOKE ALL ON TABLE biosequencefeatureattributefact FROM agrbrdf;
GRANT ALL ON TABLE biosequencefeatureattributefact TO agrbrdf;
GRANT SELECT ON TABLE biosequencefeatureattributefact TO gbs;


--
-- Name: biosequencefeaturefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosequencefeaturefact FROM PUBLIC;
REVOKE ALL ON TABLE biosequencefeaturefact FROM agrbrdf;
GRANT ALL ON TABLE biosequencefeaturefact TO agrbrdf;
GRANT SELECT ON TABLE biosequencefeaturefact TO gbs;


--
-- Name: biosequenceob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosequenceob FROM PUBLIC;
REVOKE ALL ON TABLE biosequenceob FROM agrbrdf;
GRANT ALL ON TABLE biosequenceob TO agrbrdf;
GRANT SELECT ON TABLE biosequenceob TO gbs;


--
-- Name: biosubjectfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosubjectfact FROM PUBLIC;
REVOKE ALL ON TABLE biosubjectfact FROM agrbrdf;
GRANT ALL ON TABLE biosubjectfact TO agrbrdf;
GRANT SELECT ON TABLE biosubjectfact TO gbs;


--
-- Name: biosubjectob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosubjectob FROM PUBLIC;
REVOKE ALL ON TABLE biosubjectob FROM agrbrdf;
GRANT ALL ON TABLE biosubjectob TO agrbrdf;
GRANT SELECT ON TABLE biosubjectob TO gbs;


--
-- Name: blastn_results; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE blastn_results FROM PUBLIC;
REVOKE ALL ON TABLE blastn_results FROM agrbrdf;
GRANT ALL ON TABLE blastn_results TO agrbrdf;
GRANT SELECT ON TABLE blastn_results TO gbs;


--
-- Name: blastx_results; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE blastx_results FROM PUBLIC;
REVOKE ALL ON TABLE blastx_results FROM agrbrdf;
GRANT ALL ON TABLE blastx_results TO agrbrdf;
GRANT SELECT ON TABLE blastx_results TO gbs;


--
-- Name: bovine_est_entropies; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE bovine_est_entropies FROM PUBLIC;
REVOKE ALL ON TABLE bovine_est_entropies FROM agrbrdf;
GRANT ALL ON TABLE bovine_est_entropies TO agrbrdf;
GRANT SELECT ON TABLE bovine_est_entropies TO gbs;


--
-- Name: bt4wgsnppanel_v6_3cmarkernames; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE bt4wgsnppanel_v6_3cmarkernames FROM PUBLIC;
REVOKE ALL ON TABLE bt4wgsnppanel_v6_3cmarkernames FROM agrbrdf;
GRANT ALL ON TABLE bt4wgsnppanel_v6_3cmarkernames TO agrbrdf;
GRANT SELECT ON TABLE bt4wgsnppanel_v6_3cmarkernames TO gbs;


--
-- Name: commentlink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE commentlink FROM PUBLIC;
REVOKE ALL ON TABLE commentlink FROM agrbrdf;
GRANT ALL ON TABLE commentlink TO agrbrdf;
GRANT SELECT ON TABLE commentlink TO gbs;


--
-- Name: commentob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE commentob FROM PUBLIC;
REVOKE ALL ON TABLE commentob FROM agrbrdf;
GRANT ALL ON TABLE commentob TO agrbrdf;
GRANT SELECT ON TABLE commentob TO gbs;


--
-- Name: cpgfragmentsneargenes; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE cpgfragmentsneargenes FROM PUBLIC;
REVOKE ALL ON TABLE cpgfragmentsneargenes FROM agrbrdf;
GRANT ALL ON TABLE cpgfragmentsneargenes TO agrbrdf;
GRANT SELECT ON TABLE cpgfragmentsneargenes TO gbs;


--
-- Name: cpgfragmentsneargenes_bakup; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE cpgfragmentsneargenes_bakup FROM PUBLIC;
REVOKE ALL ON TABLE cpgfragmentsneargenes_bakup FROM agrbrdf;
GRANT ALL ON TABLE cpgfragmentsneargenes_bakup TO agrbrdf;
GRANT SELECT ON TABLE cpgfragmentsneargenes_bakup TO gbs;


--
-- Name: cs34clusterpaperdata; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE cs34clusterpaperdata FROM PUBLIC;
REVOKE ALL ON TABLE cs34clusterpaperdata FROM agrbrdf;
GRANT ALL ON TABLE cs34clusterpaperdata TO agrbrdf;
GRANT SELECT ON TABLE cs34clusterpaperdata TO gbs;


--
-- Name: data_set_1_genstat_results_180908; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE data_set_1_genstat_results_180908 FROM PUBLIC;
REVOKE ALL ON TABLE data_set_1_genstat_results_180908 FROM agrbrdf;
GRANT ALL ON TABLE data_set_1_genstat_results_180908 TO agrbrdf;
GRANT SELECT ON TABLE data_set_1_genstat_results_180908 TO gbs;


--
-- Name: data_set_2_r_results_180908; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE data_set_2_r_results_180908 FROM PUBLIC;
REVOKE ALL ON TABLE data_set_2_r_results_180908 FROM agrbrdf;
GRANT ALL ON TABLE data_set_2_r_results_180908 TO agrbrdf;
GRANT SELECT ON TABLE data_set_2_r_results_180908 TO gbs;


--
-- Name: databasesearchobservation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE databasesearchobservation FROM PUBLIC;
REVOKE ALL ON TABLE databasesearchobservation FROM agrbrdf;
GRANT ALL ON TABLE databasesearchobservation TO agrbrdf;
GRANT SELECT ON TABLE databasesearchobservation TO gbs;


--
-- Name: databasesearchstudy; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE databasesearchstudy FROM PUBLIC;
REVOKE ALL ON TABLE databasesearchstudy FROM agrbrdf;
GRANT ALL ON TABLE databasesearchstudy TO agrbrdf;
GRANT SELECT ON TABLE databasesearchstudy TO gbs;


--
-- Name: datasourcefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE datasourcefact FROM PUBLIC;
REVOKE ALL ON TABLE datasourcefact FROM agrbrdf;
GRANT ALL ON TABLE datasourcefact TO agrbrdf;
GRANT SELECT ON TABLE datasourcefact TO gbs;


--
-- Name: datasourcelist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE datasourcelist FROM PUBLIC;
REVOKE ALL ON TABLE datasourcelist FROM agrbrdf;
GRANT ALL ON TABLE datasourcelist TO agrbrdf;
GRANT SELECT ON TABLE datasourcelist TO gbs;


--
-- Name: datasourcelistmembershiplink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE datasourcelistmembershiplink FROM PUBLIC;
REVOKE ALL ON TABLE datasourcelistmembershiplink FROM agrbrdf;
GRANT ALL ON TABLE datasourcelistmembershiplink TO agrbrdf;
GRANT SELECT ON TABLE datasourcelistmembershiplink TO gbs;


--
-- Name: datasourceob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE datasourceob FROM PUBLIC;
REVOKE ALL ON TABLE datasourceob FROM agrbrdf;
GRANT ALL ON TABLE datasourceob TO agrbrdf;
GRANT SELECT ON TABLE datasourceob TO gbs;


--
-- Name: displayfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE displayfunction FROM PUBLIC;
REVOKE ALL ON TABLE displayfunction FROM agrbrdf;
GRANT ALL ON TABLE displayfunction TO agrbrdf;
GRANT SELECT ON TABLE displayfunction TO gbs;


--
-- Name: displayprocedureob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE displayprocedureob FROM PUBLIC;
REVOKE ALL ON TABLE displayprocedureob FROM agrbrdf;
GRANT ALL ON TABLE displayprocedureob TO agrbrdf;
GRANT SELECT ON TABLE displayprocedureob TO gbs;


--
-- Name: keyfile_factidseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE keyfile_factidseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE keyfile_factidseq FROM agrbrdf;
GRANT ALL ON SEQUENCE keyfile_factidseq TO agrbrdf;
GRANT SELECT ON SEQUENCE keyfile_factidseq TO gbs;


--
-- Name: gbskeyfilefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE gbskeyfilefact FROM PUBLIC;
REVOKE ALL ON TABLE gbskeyfilefact FROM agrbrdf;
GRANT ALL ON TABLE gbskeyfilefact TO agrbrdf;
GRANT SELECT ON TABLE gbskeyfilefact TO gbs;


--
-- Name: gbsyieldfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE gbsyieldfact FROM PUBLIC;
REVOKE ALL ON TABLE gbsyieldfact FROM agrbrdf;
GRANT ALL ON TABLE gbsyieldfact TO agrbrdf;
GRANT SELECT ON TABLE gbsyieldfact TO gbs;


--
-- Name: gene2accession; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE gene2accession FROM PUBLIC;
REVOKE ALL ON TABLE gene2accession FROM agrbrdf;
GRANT ALL ON TABLE gene2accession TO agrbrdf;
GRANT SELECT ON TABLE gene2accession TO gbs;


--
-- Name: gene_info; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE gene_info FROM PUBLIC;
REVOKE ALL ON TABLE gene_info FROM agrbrdf;
GRANT ALL ON TABLE gene_info TO agrbrdf;
GRANT SELECT ON TABLE gene_info TO gbs;


--
-- Name: geneexpressionstudy; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneexpressionstudy FROM PUBLIC;
REVOKE ALL ON TABLE geneexpressionstudy FROM agrbrdf;
GRANT ALL ON TABLE geneexpressionstudy TO agrbrdf;
GRANT SELECT ON TABLE geneexpressionstudy TO gbs;


--
-- Name: geneexpressionstudy_backup01032009; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneexpressionstudy_backup01032009 FROM PUBLIC;
REVOKE ALL ON TABLE geneexpressionstudy_backup01032009 FROM agrbrdf;
GRANT ALL ON TABLE geneexpressionstudy_backup01032009 TO agrbrdf;
GRANT SELECT ON TABLE geneexpressionstudy_backup01032009 TO gbs;


--
-- Name: geneexpressionstudyfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneexpressionstudyfact FROM PUBLIC;
REVOKE ALL ON TABLE geneexpressionstudyfact FROM agrbrdf;
GRANT ALL ON TABLE geneexpressionstudyfact TO agrbrdf;
GRANT SELECT ON TABLE geneexpressionstudyfact TO gbs;


--
-- Name: geneproductlink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneproductlink FROM PUBLIC;
REVOKE ALL ON TABLE geneproductlink FROM agrbrdf;
GRANT ALL ON TABLE geneproductlink TO agrbrdf;
GRANT SELECT ON TABLE geneproductlink TO gbs;


--
-- Name: generegulationlink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE generegulationlink FROM PUBLIC;
REVOKE ALL ON TABLE generegulationlink FROM agrbrdf;
GRANT ALL ON TABLE generegulationlink TO agrbrdf;
GRANT SELECT ON TABLE generegulationlink TO gbs;


--
-- Name: geneticexpressionfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticexpressionfact FROM PUBLIC;
REVOKE ALL ON TABLE geneticexpressionfact FROM agrbrdf;
GRANT ALL ON TABLE geneticexpressionfact TO agrbrdf;
GRANT SELECT ON TABLE geneticexpressionfact TO gbs;


--
-- Name: geneticfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticfact FROM PUBLIC;
REVOKE ALL ON TABLE geneticfact FROM agrbrdf;
GRANT ALL ON TABLE geneticfact TO agrbrdf;
GRANT SELECT ON TABLE geneticfact TO gbs;


--
-- Name: geneticfunctionfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticfunctionfact FROM PUBLIC;
REVOKE ALL ON TABLE geneticfunctionfact FROM agrbrdf;
GRANT ALL ON TABLE geneticfunctionfact TO agrbrdf;
GRANT SELECT ON TABLE geneticfunctionfact TO gbs;


--
-- Name: geneticlocationfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticlocationfact FROM PUBLIC;
REVOKE ALL ON TABLE geneticlocationfact FROM agrbrdf;
GRANT ALL ON TABLE geneticlocationfact TO agrbrdf;
GRANT SELECT ON TABLE geneticlocationfact TO gbs;


--
-- Name: geneticlocationlist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticlocationlist FROM PUBLIC;
REVOKE ALL ON TABLE geneticlocationlist FROM agrbrdf;
GRANT ALL ON TABLE geneticlocationlist TO agrbrdf;
GRANT SELECT ON TABLE geneticlocationlist TO gbs;


--
-- Name: geneticlocationlistmembershiplink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticlocationlistmembershiplink FROM PUBLIC;
REVOKE ALL ON TABLE geneticlocationlistmembershiplink FROM agrbrdf;
GRANT ALL ON TABLE geneticlocationlistmembershiplink TO agrbrdf;
GRANT SELECT ON TABLE geneticlocationlistmembershiplink TO gbs;


--
-- Name: geneticob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticob FROM PUBLIC;
REVOKE ALL ON TABLE geneticob FROM agrbrdf;
GRANT ALL ON TABLE geneticob TO agrbrdf;
GRANT SELECT ON TABLE geneticob TO gbs;


--
-- Name: geneticoblist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticoblist FROM PUBLIC;
REVOKE ALL ON TABLE geneticoblist FROM agrbrdf;
GRANT ALL ON TABLE geneticoblist TO agrbrdf;
GRANT SELECT ON TABLE geneticoblist TO gbs;


--
-- Name: geneticoblistmembershiplink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticoblistmembershiplink FROM PUBLIC;
REVOKE ALL ON TABLE geneticoblistmembershiplink FROM agrbrdf;
GRANT ALL ON TABLE geneticoblistmembershiplink TO agrbrdf;
GRANT SELECT ON TABLE geneticoblistmembershiplink TO gbs;


--
-- Name: genetictestfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genetictestfact FROM PUBLIC;
REVOKE ALL ON TABLE genetictestfact FROM agrbrdf;
GRANT ALL ON TABLE genetictestfact TO agrbrdf;
GRANT SELECT ON TABLE genetictestfact TO gbs;


--
-- Name: genetictestfact2; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genetictestfact2 FROM PUBLIC;
REVOKE ALL ON TABLE genetictestfact2 FROM agrbrdf;
GRANT ALL ON TABLE genetictestfact2 TO agrbrdf;
GRANT SELECT ON TABLE genetictestfact2 TO gbs;


--
-- Name: genotypeobservation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genotypeobservation FROM PUBLIC;
REVOKE ALL ON TABLE genotypeobservation FROM agrbrdf;
GRANT ALL ON TABLE genotypeobservation TO agrbrdf;
GRANT SELECT ON TABLE genotypeobservation TO gbs;


--
-- Name: genotypeobservationfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genotypeobservationfact FROM PUBLIC;
REVOKE ALL ON TABLE genotypeobservationfact FROM agrbrdf;
GRANT ALL ON TABLE genotypeobservationfact TO agrbrdf;
GRANT SELECT ON TABLE genotypeobservationfact TO gbs;


--
-- Name: genotypes; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genotypes FROM PUBLIC;
REVOKE ALL ON TABLE genotypes FROM agrbrdf;
GRANT ALL ON TABLE genotypes TO agrbrdf;
GRANT SELECT ON TABLE genotypes TO gbs;


--
-- Name: genotypestudy; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genotypestudy FROM PUBLIC;
REVOKE ALL ON TABLE genotypestudy FROM agrbrdf;
GRANT ALL ON TABLE genotypestudy TO agrbrdf;
GRANT SELECT ON TABLE genotypestudy TO gbs;


--
-- Name: genotypestudyfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genotypestudyfact FROM PUBLIC;
REVOKE ALL ON TABLE genotypestudyfact FROM agrbrdf;
GRANT ALL ON TABLE genotypestudyfact TO agrbrdf;
GRANT SELECT ON TABLE genotypestudyfact TO gbs;


--
-- Name: geosubmissiondata; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geosubmissiondata FROM PUBLIC;
REVOKE ALL ON TABLE geosubmissiondata FROM agrbrdf;
GRANT ALL ON TABLE geosubmissiondata TO agrbrdf;
GRANT SELECT ON TABLE geosubmissiondata TO gbs;


--
-- Name: gpl3802_annotation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE gpl3802_annotation FROM PUBLIC;
REVOKE ALL ON TABLE gpl3802_annotation FROM agrbrdf;
GRANT ALL ON TABLE gpl3802_annotation TO agrbrdf;
GRANT SELECT ON TABLE gpl3802_annotation TO gbs;


--
-- Name: gpl7083_34008annotation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE gpl7083_34008annotation FROM PUBLIC;
REVOKE ALL ON TABLE gpl7083_34008annotation FROM agrbrdf;
GRANT ALL ON TABLE gpl7083_34008annotation TO agrbrdf;
GRANT SELECT ON TABLE gpl7083_34008annotation TO gbs;


--
-- Name: harvestwheatchip_annotation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE harvestwheatchip_annotation FROM PUBLIC;
REVOKE ALL ON TABLE harvestwheatchip_annotation FROM agrbrdf;
GRANT ALL ON TABLE harvestwheatchip_annotation TO agrbrdf;
GRANT SELECT ON TABLE harvestwheatchip_annotation TO gbs;


--
-- Name: hg18_cpg_location; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE hg18_cpg_location FROM PUBLIC;
REVOKE ALL ON TABLE hg18_cpg_location FROM agrbrdf;
GRANT ALL ON TABLE hg18_cpg_location TO agrbrdf;
GRANT SELECT ON TABLE hg18_cpg_location TO gbs;


--
-- Name: hg18_cpg_mspi_overlap; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE hg18_cpg_mspi_overlap FROM PUBLIC;
REVOKE ALL ON TABLE hg18_cpg_mspi_overlap FROM agrbrdf;
GRANT ALL ON TABLE hg18_cpg_mspi_overlap TO agrbrdf;
GRANT SELECT ON TABLE hg18_cpg_mspi_overlap TO gbs;


--
-- Name: hg18_cpg_mspi_overlap_bakup; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE hg18_cpg_mspi_overlap_bakup FROM PUBLIC;
REVOKE ALL ON TABLE hg18_cpg_mspi_overlap_bakup FROM agrbrdf;
GRANT ALL ON TABLE hg18_cpg_mspi_overlap_bakup TO agrbrdf;
GRANT SELECT ON TABLE hg18_cpg_mspi_overlap_bakup TO gbs;


--
-- Name: hg18_mspi_digest; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE hg18_mspi_digest FROM PUBLIC;
REVOKE ALL ON TABLE hg18_mspi_digest FROM agrbrdf;
GRANT ALL ON TABLE hg18_mspi_digest TO agrbrdf;
GRANT SELECT ON TABLE hg18_mspi_digest TO gbs;


--
-- Name: hg18_refgenes_location; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE hg18_refgenes_location FROM PUBLIC;
REVOKE ALL ON TABLE hg18_refgenes_location FROM agrbrdf;
GRANT ALL ON TABLE hg18_refgenes_location TO agrbrdf;
GRANT SELECT ON TABLE hg18_refgenes_location TO gbs;


--
-- Name: hg18uniquereads; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE hg18uniquereads FROM PUBLIC;
REVOKE ALL ON TABLE hg18uniquereads FROM agrbrdf;
GRANT ALL ON TABLE hg18uniquereads TO agrbrdf;
GRANT SELECT ON TABLE hg18uniquereads TO gbs;


--
-- Name: samplesheet_factidseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE samplesheet_factidseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE samplesheet_factidseq FROM agrbrdf;
GRANT ALL ON SEQUENCE samplesheet_factidseq TO agrbrdf;
GRANT SELECT ON SEQUENCE samplesheet_factidseq TO gbs;


--
-- Name: hiseqsamplesheetfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE hiseqsamplesheetfact FROM PUBLIC;
REVOKE ALL ON TABLE hiseqsamplesheetfact FROM agrbrdf;
GRANT ALL ON TABLE hiseqsamplesheetfact TO agrbrdf;
GRANT SELECT ON TABLE hiseqsamplesheetfact TO gbs;


--
-- Name: humanplacentalorthologs; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE humanplacentalorthologs FROM PUBLIC;
REVOKE ALL ON TABLE humanplacentalorthologs FROM agrbrdf;
GRANT ALL ON TABLE humanplacentalorthologs TO agrbrdf;
GRANT SELECT ON TABLE humanplacentalorthologs TO gbs;


--
-- Name: importfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE importfunction FROM PUBLIC;
REVOKE ALL ON TABLE importfunction FROM agrbrdf;
GRANT ALL ON TABLE importfunction TO agrbrdf;
GRANT SELECT ON TABLE importfunction TO gbs;


--
-- Name: importfunctionfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE importfunctionfact FROM PUBLIC;
REVOKE ALL ON TABLE importfunctionfact FROM agrbrdf;
GRANT ALL ON TABLE importfunctionfact TO agrbrdf;
GRANT SELECT ON TABLE importfunctionfact TO gbs;


--
-- Name: importprocedureob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE importprocedureob FROM PUBLIC;
REVOKE ALL ON TABLE importprocedureob FROM agrbrdf;
GRANT ALL ON TABLE importprocedureob TO agrbrdf;
GRANT SELECT ON TABLE importprocedureob TO gbs;


--
-- Name: junk; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE junk FROM PUBLIC;
REVOKE ALL ON TABLE junk FROM agrbrdf;
GRANT ALL ON TABLE junk TO agrbrdf;
GRANT SELECT ON TABLE junk TO gbs;


--
-- Name: junk1; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE junk1 FROM PUBLIC;
REVOKE ALL ON TABLE junk1 FROM agrbrdf;
GRANT ALL ON TABLE junk1 TO agrbrdf;
GRANT SELECT ON TABLE junk1 TO gbs;


--
-- Name: keyfile_temp; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE keyfile_temp FROM PUBLIC;
REVOKE ALL ON TABLE keyfile_temp FROM agrbrdf;
GRANT ALL ON TABLE keyfile_temp TO agrbrdf;
GRANT SELECT ON TABLE keyfile_temp TO gbs;


--
-- Name: keyfile_temp_nofastq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE keyfile_temp_nofastq FROM PUBLIC;
REVOKE ALL ON TABLE keyfile_temp_nofastq FROM agrbrdf;
GRANT ALL ON TABLE keyfile_temp_nofastq TO agrbrdf;
GRANT SELECT ON TABLE keyfile_temp_nofastq TO gbs;


--
-- Name: labresourcefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE labresourcefact FROM PUBLIC;
REVOKE ALL ON TABLE labresourcefact FROM agrbrdf;
GRANT ALL ON TABLE labresourcefact TO agrbrdf;
GRANT SELECT ON TABLE labresourcefact TO gbs;


--
-- Name: labresourcelist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE labresourcelist FROM PUBLIC;
REVOKE ALL ON TABLE labresourcelist FROM agrbrdf;
GRANT ALL ON TABLE labresourcelist TO agrbrdf;
GRANT SELECT ON TABLE labresourcelist TO gbs;


--
-- Name: labresourcelistmembershiplink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE labresourcelistmembershiplink FROM PUBLIC;
REVOKE ALL ON TABLE labresourcelistmembershiplink FROM agrbrdf;
GRANT ALL ON TABLE labresourcelistmembershiplink TO agrbrdf;
GRANT SELECT ON TABLE labresourcelistmembershiplink TO gbs;


--
-- Name: labresourceob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE labresourceob FROM PUBLIC;
REVOKE ALL ON TABLE labresourceob FROM agrbrdf;
GRANT ALL ON TABLE labresourceob TO agrbrdf;
GRANT SELECT ON TABLE labresourceob TO gbs;


--
-- Name: librarysequencingfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE librarysequencingfact FROM PUBLIC;
REVOKE ALL ON TABLE librarysequencingfact FROM agrbrdf;
GRANT ALL ON TABLE librarysequencingfact TO agrbrdf;
GRANT SELECT ON TABLE librarysequencingfact TO gbs;


--
-- Name: librarysequencingfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE librarysequencingfunction FROM PUBLIC;
REVOKE ALL ON TABLE librarysequencingfunction FROM agrbrdf;
GRANT ALL ON TABLE librarysequencingfunction TO agrbrdf;
GRANT SELECT ON TABLE librarysequencingfunction TO gbs;


--
-- Name: licexpression1; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE licexpression1 FROM PUBLIC;
REVOKE ALL ON TABLE licexpression1 FROM agrbrdf;
GRANT ALL ON TABLE licexpression1 TO agrbrdf;
GRANT SELECT ON TABLE licexpression1 TO gbs;


--
-- Name: licnormalisation1; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE licnormalisation1 FROM PUBLIC;
REVOKE ALL ON TABLE licnormalisation1 FROM agrbrdf;
GRANT ALL ON TABLE licnormalisation1 TO agrbrdf;
GRANT SELECT ON TABLE licnormalisation1 TO gbs;


--
-- Name: lindawheat1; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE lindawheat1 FROM PUBLIC;
REVOKE ALL ON TABLE lindawheat1 FROM agrbrdf;
GRANT ALL ON TABLE lindawheat1 TO agrbrdf;
GRANT SELECT ON TABLE lindawheat1 TO gbs;


--
-- Name: lisafan_expt136_lowscan_no_bg_corr_delete01102008; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE lisafan_expt136_lowscan_no_bg_corr_delete01102008 FROM PUBLIC;
REVOKE ALL ON TABLE lisafan_expt136_lowscan_no_bg_corr_delete01102008 FROM agrbrdf;
GRANT ALL ON TABLE lisafan_expt136_lowscan_no_bg_corr_delete01102008 TO agrbrdf;
GRANT SELECT ON TABLE lisafan_expt136_lowscan_no_bg_corr_delete01102008 TO gbs;


--
-- Name: lisafanseriesnormalisation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE lisafanseriesnormalisation FROM PUBLIC;
REVOKE ALL ON TABLE lisafanseriesnormalisation FROM agrbrdf;
GRANT ALL ON TABLE lisafanseriesnormalisation TO agrbrdf;
GRANT SELECT ON TABLE lisafanseriesnormalisation TO gbs;


--
-- Name: lisafanseriesnormalisation_backup23092008; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE lisafanseriesnormalisation_backup23092008 FROM PUBLIC;
REVOKE ALL ON TABLE lisafanseriesnormalisation_backup23092008 FROM agrbrdf;
GRANT ALL ON TABLE lisafanseriesnormalisation_backup23092008 TO agrbrdf;
GRANT SELECT ON TABLE lisafanseriesnormalisation_backup23092008 TO gbs;


--
-- Name: listorderseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE listorderseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE listorderseq FROM agrbrdf;
GRANT ALL ON SEQUENCE listorderseq TO agrbrdf;
GRANT SELECT,UPDATE ON SEQUENCE listorderseq TO gbs;


--
-- Name: lmf_factidseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE lmf_factidseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE lmf_factidseq FROM agrbrdf;
GRANT ALL ON SEQUENCE lmf_factidseq TO agrbrdf;
GRANT SELECT ON SEQUENCE lmf_factidseq TO gbs;


--
-- Name: listmembershipfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE listmembershipfact FROM PUBLIC;
REVOKE ALL ON TABLE listmembershipfact FROM agrbrdf;
GRANT ALL ON TABLE listmembershipfact TO agrbrdf;
GRANT SELECT ON TABLE listmembershipfact TO gbs;


--
-- Name: listmembershiplink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE listmembershiplink FROM PUBLIC;
REVOKE ALL ON TABLE listmembershiplink FROM agrbrdf;
GRANT ALL ON TABLE listmembershiplink TO agrbrdf;
GRANT SELECT,INSERT,DELETE ON TABLE listmembershiplink TO gbs;


--
-- Name: literaturereferencelink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE literaturereferencelink FROM PUBLIC;
REVOKE ALL ON TABLE literaturereferencelink FROM agrbrdf;
GRANT ALL ON TABLE literaturereferencelink TO agrbrdf;
GRANT SELECT ON TABLE literaturereferencelink TO gbs;


--
-- Name: literaturereferenceob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE literaturereferenceob FROM PUBLIC;
REVOKE ALL ON TABLE literaturereferenceob FROM agrbrdf;
GRANT ALL ON TABLE literaturereferenceob TO agrbrdf;
GRANT SELECT ON TABLE literaturereferenceob TO gbs;


--
-- Name: miamefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE miamefact FROM PUBLIC;
REVOKE ALL ON TABLE miamefact FROM agrbrdf;
GRANT ALL ON TABLE miamefact TO agrbrdf;
GRANT SELECT ON TABLE miamefact TO gbs;


--
-- Name: microarrayfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE microarrayfact FROM PUBLIC;
REVOKE ALL ON TABLE microarrayfact FROM agrbrdf;
GRANT ALL ON TABLE microarrayfact TO agrbrdf;
GRANT SELECT ON TABLE microarrayfact TO gbs;


--
-- Name: microarrayobservation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE microarrayobservation FROM PUBLIC;
REVOKE ALL ON TABLE microarrayobservation FROM agrbrdf;
GRANT ALL ON TABLE microarrayobservation TO agrbrdf;
GRANT SELECT ON TABLE microarrayobservation TO gbs;


--
-- Name: microarrayobservationfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE microarrayobservationfact FROM PUBLIC;
REVOKE ALL ON TABLE microarrayobservationfact FROM agrbrdf;
GRANT ALL ON TABLE microarrayobservationfact TO agrbrdf;
GRANT SELECT ON TABLE microarrayobservationfact TO gbs;


--
-- Name: microarrayspotfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE microarrayspotfact FROM PUBLIC;
REVOKE ALL ON TABLE microarrayspotfact FROM agrbrdf;
GRANT ALL ON TABLE microarrayspotfact TO agrbrdf;
GRANT SELECT ON TABLE microarrayspotfact TO gbs;


--
-- Name: mylogger; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE mylogger FROM PUBLIC;
REVOKE ALL ON TABLE mylogger FROM agrbrdf;
GRANT ALL ON TABLE mylogger TO agrbrdf;
GRANT SELECT ON TABLE mylogger TO gbs;


--
-- Name: ob_obidseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE ob_obidseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE ob_obidseq FROM agrbrdf;
GRANT ALL ON SEQUENCE ob_obidseq TO agrbrdf;
GRANT SELECT,UPDATE ON SEQUENCE ob_obidseq TO gbs;


--
-- Name: oblist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE oblist FROM PUBLIC;
REVOKE ALL ON TABLE oblist FROM agrbrdf;
GRANT ALL ON TABLE oblist TO agrbrdf;
GRANT SELECT,INSERT,DELETE ON TABLE oblist TO gbs;


--
-- Name: oblistfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE oblistfact FROM PUBLIC;
REVOKE ALL ON TABLE oblistfact FROM agrbrdf;
GRANT ALL ON TABLE oblistfact TO agrbrdf;
GRANT SELECT ON TABLE oblistfact TO gbs;


--
-- Name: obstatus; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE obstatus FROM PUBLIC;
REVOKE ALL ON TABLE obstatus FROM agrbrdf;
GRANT ALL ON TABLE obstatus TO agrbrdf;
GRANT SELECT ON TABLE obstatus TO gbs;


--
-- Name: obtype; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE obtype FROM PUBLIC;
REVOKE ALL ON TABLE obtype FROM agrbrdf;
GRANT ALL ON TABLE obtype TO agrbrdf;
GRANT SELECT ON TABLE obtype TO gbs;


--
-- Name: obtype_obtypeidseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE obtype_obtypeidseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE obtype_obtypeidseq FROM agrbrdf;
GRANT ALL ON SEQUENCE obtype_obtypeidseq TO agrbrdf;
GRANT SELECT ON SEQUENCE obtype_obtypeidseq TO gbs;


--
-- Name: obtypesignature; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE obtypesignature FROM PUBLIC;
REVOKE ALL ON TABLE obtypesignature FROM agrbrdf;
GRANT ALL ON TABLE obtypesignature TO agrbrdf;
GRANT SELECT ON TABLE obtypesignature TO gbs;


--
-- Name: ontologyfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE ontologyfact FROM PUBLIC;
REVOKE ALL ON TABLE ontologyfact FROM agrbrdf;
GRANT ALL ON TABLE ontologyfact TO agrbrdf;
GRANT SELECT ON TABLE ontologyfact TO gbs;


--
-- Name: ontologyob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE ontologyob FROM PUBLIC;
REVOKE ALL ON TABLE ontologyob FROM agrbrdf;
GRANT ALL ON TABLE ontologyob TO agrbrdf;
GRANT SELECT ON TABLE ontologyob TO gbs;


--
-- Name: ontologytermfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE ontologytermfact FROM PUBLIC;
REVOKE ALL ON TABLE ontologytermfact FROM agrbrdf;
GRANT ALL ON TABLE ontologytermfact TO agrbrdf;
GRANT SELECT ON TABLE ontologytermfact TO gbs;


--
-- Name: ontologytermfact2; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE ontologytermfact2 FROM PUBLIC;
REVOKE ALL ON TABLE ontologytermfact2 FROM agrbrdf;
GRANT ALL ON TABLE ontologytermfact2 TO agrbrdf;
GRANT SELECT ON TABLE ontologytermfact2 TO gbs;


--
-- Name: optypesignature; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE optypesignature FROM PUBLIC;
REVOKE ALL ON TABLE optypesignature FROM agrbrdf;
GRANT ALL ON TABLE optypesignature TO agrbrdf;
GRANT SELECT ON TABLE optypesignature TO gbs;


--
-- Name: oracle_microarray_experiment; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE oracle_microarray_experiment FROM PUBLIC;
REVOKE ALL ON TABLE oracle_microarray_experiment FROM agrbrdf;
GRANT ALL ON TABLE oracle_microarray_experiment TO agrbrdf;
GRANT SELECT ON TABLE oracle_microarray_experiment TO gbs;


--
-- Name: oracle_seqsource; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE oracle_seqsource FROM PUBLIC;
REVOKE ALL ON TABLE oracle_seqsource FROM agrbrdf;
GRANT ALL ON TABLE oracle_seqsource TO agrbrdf;
GRANT SELECT ON TABLE oracle_seqsource TO gbs;


--
-- Name: pedigreelink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE pedigreelink FROM PUBLIC;
REVOKE ALL ON TABLE pedigreelink FROM agrbrdf;
GRANT ALL ON TABLE pedigreelink TO agrbrdf;
GRANT SELECT ON TABLE pedigreelink TO gbs;


--
-- Name: phenotypeobservation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE phenotypeobservation FROM PUBLIC;
REVOKE ALL ON TABLE phenotypeobservation FROM agrbrdf;
GRANT ALL ON TABLE phenotypeobservation TO agrbrdf;
GRANT SELECT ON TABLE phenotypeobservation TO gbs;


--
-- Name: phenotypestudy; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE phenotypestudy FROM PUBLIC;
REVOKE ALL ON TABLE phenotypestudy FROM agrbrdf;
GRANT ALL ON TABLE phenotypestudy TO agrbrdf;
GRANT SELECT ON TABLE phenotypestudy TO gbs;


--
-- Name: platypusorthologs; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE platypusorthologs FROM PUBLIC;
REVOKE ALL ON TABLE platypusorthologs FROM agrbrdf;
GRANT ALL ON TABLE platypusorthologs TO agrbrdf;
GRANT SELECT ON TABLE platypusorthologs TO gbs;


--
-- Name: possumjunk1; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE possumjunk1 FROM PUBLIC;
REVOKE ALL ON TABLE possumjunk1 FROM agrbrdf;
GRANT ALL ON TABLE possumjunk1 TO agrbrdf;
GRANT SELECT ON TABLE possumjunk1 TO gbs;


--
-- Name: possumjunk3; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE possumjunk3 FROM PUBLIC;
REVOKE ALL ON TABLE possumjunk3 FROM agrbrdf;
GRANT ALL ON TABLE possumjunk3 TO agrbrdf;
GRANT SELECT ON TABLE possumjunk3 TO gbs;


--
-- Name: predicatelink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE predicatelink FROM PUBLIC;
REVOKE ALL ON TABLE predicatelink FROM agrbrdf;
GRANT ALL ON TABLE predicatelink TO agrbrdf;
GRANT SELECT ON TABLE predicatelink TO gbs;


--
-- Name: predicatelinkfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE predicatelinkfact FROM PUBLIC;
REVOKE ALL ON TABLE predicatelinkfact FROM agrbrdf;
GRANT ALL ON TABLE predicatelinkfact TO agrbrdf;
GRANT SELECT ON TABLE predicatelinkfact TO gbs;


--
-- Name: print139annotation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE print139annotation FROM PUBLIC;
REVOKE ALL ON TABLE print139annotation FROM agrbrdf;
GRANT ALL ON TABLE print139annotation TO agrbrdf;
GRANT SELECT ON TABLE print139annotation TO gbs;


--
-- Name: print139annotation_v1; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE print139annotation_v1 FROM PUBLIC;
REVOKE ALL ON TABLE print139annotation_v1 FROM agrbrdf;
GRANT ALL ON TABLE print139annotation_v1 TO agrbrdf;
GRANT SELECT ON TABLE print139annotation_v1 TO gbs;


--
-- Name: print139annotationbackup; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE print139annotationbackup FROM PUBLIC;
REVOKE ALL ON TABLE print139annotationbackup FROM agrbrdf;
GRANT ALL ON TABLE print139annotationbackup TO agrbrdf;
GRANT SELECT ON TABLE print139annotationbackup TO gbs;


--
-- Name: print139annotationbackup2; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE print139annotationbackup2 FROM PUBLIC;
REVOKE ALL ON TABLE print139annotationbackup2 FROM agrbrdf;
GRANT ALL ON TABLE print139annotationbackup2 TO agrbrdf;
GRANT SELECT ON TABLE print139annotationbackup2 TO gbs;


--
-- Name: reproductionmicroarrayplasmids; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE reproductionmicroarrayplasmids FROM PUBLIC;
REVOKE ALL ON TABLE reproductionmicroarrayplasmids FROM agrbrdf;
GRANT ALL ON TABLE reproductionmicroarrayplasmids TO agrbrdf;
GRANT SELECT ON TABLE reproductionmicroarrayplasmids TO gbs;


--
-- Name: samplesheet_temp; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE samplesheet_temp FROM PUBLIC;
REVOKE ALL ON TABLE samplesheet_temp FROM agrbrdf;
GRANT ALL ON TABLE samplesheet_temp TO agrbrdf;
GRANT SELECT ON TABLE samplesheet_temp TO gbs;


--
-- Name: scratch; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE scratch FROM PUBLIC;
REVOKE ALL ON TABLE scratch FROM agrbrdf;
GRANT ALL ON TABLE scratch TO agrbrdf;
GRANT SELECT ON TABLE scratch TO gbs;


--
-- Name: securityfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE securityfunction FROM PUBLIC;
REVOKE ALL ON TABLE securityfunction FROM agrbrdf;
GRANT ALL ON TABLE securityfunction TO agrbrdf;
GRANT SELECT ON TABLE securityfunction TO gbs;


--
-- Name: securityprocedureob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE securityprocedureob FROM PUBLIC;
REVOKE ALL ON TABLE securityprocedureob FROM agrbrdf;
GRANT ALL ON TABLE securityprocedureob TO agrbrdf;
GRANT SELECT ON TABLE securityprocedureob TO gbs;


--
-- Name: sequencealignmentfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE sequencealignmentfact FROM PUBLIC;
REVOKE ALL ON TABLE sequencealignmentfact FROM agrbrdf;
GRANT ALL ON TABLE sequencealignmentfact TO agrbrdf;
GRANT SELECT ON TABLE sequencealignmentfact TO gbs;


--
-- Name: sequencingfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE sequencingfact FROM PUBLIC;
REVOKE ALL ON TABLE sequencingfact FROM agrbrdf;
GRANT ALL ON TABLE sequencingfact TO agrbrdf;
GRANT SELECT ON TABLE sequencingfact TO gbs;


--
-- Name: sequencingfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE sequencingfunction FROM PUBLIC;
REVOKE ALL ON TABLE sequencingfunction FROM agrbrdf;
GRANT ALL ON TABLE sequencingfunction TO agrbrdf;
GRANT SELECT ON TABLE sequencingfunction TO gbs;


--
-- Name: sheepv3_prot_annotation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE sheepv3_prot_annotation FROM PUBLIC;
REVOKE ALL ON TABLE sheepv3_prot_annotation FROM agrbrdf;
GRANT ALL ON TABLE sheepv3_prot_annotation TO agrbrdf;
GRANT SELECT ON TABLE sheepv3_prot_annotation TO gbs;


--
-- Name: spotidmapcaco2; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE spotidmapcaco2 FROM PUBLIC;
REVOKE ALL ON TABLE spotidmapcaco2 FROM agrbrdf;
GRANT ALL ON TABLE spotidmapcaco2 TO agrbrdf;
GRANT SELECT ON TABLE spotidmapcaco2 TO gbs;


--
-- Name: stafffact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE stafffact FROM PUBLIC;
REVOKE ALL ON TABLE stafffact FROM agrbrdf;
GRANT ALL ON TABLE stafffact TO agrbrdf;
GRANT SELECT ON TABLE stafffact TO gbs;


--
-- Name: staffob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE staffob FROM PUBLIC;
REVOKE ALL ON TABLE staffob FROM agrbrdf;
GRANT ALL ON TABLE staffob TO agrbrdf;
GRANT SELECT ON TABLE staffob TO gbs;


--
-- Name: t_animal_fact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE t_animal_fact FROM PUBLIC;
REVOKE ALL ON TABLE t_animal_fact FROM agrbrdf;
GRANT ALL ON TABLE t_animal_fact TO agrbrdf;
GRANT SELECT ON TABLE t_animal_fact TO gbs;


--
-- Name: t_sample_fact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE t_sample_fact FROM PUBLIC;
REVOKE ALL ON TABLE t_sample_fact FROM agrbrdf;
GRANT ALL ON TABLE t_sample_fact TO agrbrdf;
GRANT SELECT ON TABLE t_sample_fact TO gbs;


--
-- Name: taxonomy_names; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE taxonomy_names FROM PUBLIC;
REVOKE ALL ON TABLE taxonomy_names FROM agrbrdf;
GRANT ALL ON TABLE taxonomy_names TO agrbrdf;
GRANT SELECT ON TABLE taxonomy_names TO gbs;


--
-- Name: urilink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE urilink FROM PUBLIC;
REVOKE ALL ON TABLE urilink FROM agrbrdf;
GRANT ALL ON TABLE urilink TO agrbrdf;
GRANT SELECT ON TABLE urilink TO gbs;


--
-- Name: uriob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE uriob FROM PUBLIC;
REVOKE ALL ON TABLE uriob FROM agrbrdf;
GRANT ALL ON TABLE uriob TO agrbrdf;
GRANT SELECT ON TABLE uriob TO gbs;


--
-- Name: wheatchipannotation2011; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE wheatchipannotation2011 FROM PUBLIC;
REVOKE ALL ON TABLE wheatchipannotation2011 FROM agrbrdf;
GRANT ALL ON TABLE wheatchipannotation2011 TO agrbrdf;
GRANT SELECT ON TABLE wheatchipannotation2011 TO gbs;


--
-- Name: wheatrma; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE wheatrma FROM PUBLIC;
REVOKE ALL ON TABLE wheatrma FROM agrbrdf;
GRANT ALL ON TABLE wheatrma TO agrbrdf;
GRANT SELECT ON TABLE wheatrma TO gbs;


--
-- Name: workflowlink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE workflowlink FROM PUBLIC;
REVOKE ALL ON TABLE workflowlink FROM agrbrdf;
GRANT ALL ON TABLE workflowlink TO agrbrdf;
GRANT SELECT ON TABLE workflowlink TO gbs;


--
-- Name: workflowmembershiplink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE workflowmembershiplink FROM PUBLIC;
REVOKE ALL ON TABLE workflowmembershiplink FROM agrbrdf;
GRANT ALL ON TABLE workflowmembershiplink TO agrbrdf;
GRANT SELECT ON TABLE workflowmembershiplink TO gbs;


--
-- Name: workflowob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE workflowob FROM PUBLIC;
REVOKE ALL ON TABLE workflowob FROM agrbrdf;
GRANT ALL ON TABLE workflowob TO agrbrdf;
GRANT SELECT ON TABLE workflowob TO gbs;


--
-- Name: workflowstageob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE workflowstageob FROM PUBLIC;
REVOKE ALL ON TABLE workflowstageob FROM agrbrdf;
GRANT ALL ON TABLE workflowstageob TO agrbrdf;
GRANT SELECT ON TABLE workflowstageob TO gbs;


--
-- Name: workstagevisitfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE workstagevisitfact FROM PUBLIC;
REVOKE ALL ON TABLE workstagevisitfact FROM agrbrdf;
GRANT ALL ON TABLE workstagevisitfact TO agrbrdf;
GRANT SELECT ON TABLE workstagevisitfact TO gbs;


--
-- PostgreSQL database dump complete
--

