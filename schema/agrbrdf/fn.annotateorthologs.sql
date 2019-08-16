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

