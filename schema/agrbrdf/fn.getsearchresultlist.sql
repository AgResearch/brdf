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

