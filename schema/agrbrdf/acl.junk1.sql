--
-- Name: junk1; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE junk1 FROM PUBLIC;
REVOKE ALL ON TABLE junk1 FROM agrbrdf;
GRANT ALL ON TABLE junk1 TO agrbrdf;
GRANT SELECT ON TABLE junk1 TO gbs;


