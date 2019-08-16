--
-- Name: pedigreelink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE pedigreelink FROM PUBLIC;
REVOKE ALL ON TABLE pedigreelink FROM agrbrdf;
GRANT ALL ON TABLE pedigreelink TO agrbrdf;
GRANT SELECT ON TABLE pedigreelink TO gbs;


