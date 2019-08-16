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

