--
-- Name: junk; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE junk FROM PUBLIC;
REVOKE ALL ON TABLE junk FROM agrbrdf;
GRANT ALL ON TABLE junk TO agrbrdf;
GRANT SELECT ON TABLE junk TO gbs;


