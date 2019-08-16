--
-- Name: hiseqsamplesheetfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE hiseqsamplesheetfact FROM PUBLIC;
REVOKE ALL ON TABLE hiseqsamplesheetfact FROM agrbrdf;
GRANT ALL ON TABLE hiseqsamplesheetfact TO agrbrdf;
GRANT SELECT ON TABLE hiseqsamplesheetfact TO gbs;


