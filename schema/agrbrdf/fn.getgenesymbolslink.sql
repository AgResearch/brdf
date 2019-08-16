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

